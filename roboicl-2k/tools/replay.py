"""Replay saved policy actions through the unchanged official 30 Hz evaluator.

No model API is contacted. Original observations and physics are retained;
independent high-resolution cameras render recorded poses after validation.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import pickle
import runpy
import shutil
import subprocess
import sys
import time

import numpy as np
from scene_recording import SceneRecording, dump, read

EVALUATOR = Path('/cpfs01/zijian.pan/eval_30hz')
REPO = Path('/cpfs01/shenyq/repo/starVLA_domino_qwen3_ablation')


def actions_from_source(source, report):
    trace = [json.loads(s) for s in (source/'action_trace.jsonl').read_text().splitlines() if s]
    assert [r['action_index'] for r in trace] == list(range(1, len(trace)+1))
    actions = [r['target'] for r in trace]
    recovered = []
    if len(actions) != report['steps']:
        # SD2 can raise during the final action, before the trace append.
        decisions_path, = source.parents[1].glob('astra/*/decisions.jsonl')
        decisions = [json.loads(s) for s in decisions_path.read_text().splitlines() if s]
        for step in range(len(actions), report['steps']):
            decision = max((r for r in decisions if r['step'] <= step), key=lambda r:r['step'])
            offset = step-decision['step']
            a = decision['requested_actions'][offset]
            assert a['mode'] == 'joint'
            target = np.asarray(a['left']+[a['left_gripper']]+a['right']+[a['right_gripper']], dtype=np.float32).tolist()
            # Check the same extraction against the preceding logged actions.
            for prior in range(decision['step'], step):
                d = decision['requested_actions'][prior-decision['step']]
                check = np.asarray(d['left']+[d['left_gripper']]+d['right']+[d['right_gripper']], dtype=np.float32)
                assert np.array_equal(check, np.asarray(actions[prior]))
            actions.append(target)
            recovered.append(dict(action_index=step+1, decision_step=decision['step'], chunk_offset=offset,
                                  source=str(decisions_path), target=target))
    assert len(actions) == report['steps']
    return trace, actions, recovered


def compare_values(a, b, path='', mismatches=None):
    if mismatches is None: mismatches = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in a:
            if k not in b: mismatches.append(path+'.'+k+': missing')
            else: compare_values(a[k], b[k], path+'.'+k, mismatches)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b): mismatches.append(path+': length')
        else:
            for i,(x,y) in enumerate(zip(a,b)): compare_values(x,y,f'{path}[{i}]',mismatches)
    elif isinstance(a, int) and isinstance(b, int):
        if a != b: mismatches.append(f'{path}: {a} != {b}')
    elif isinstance(a, (float,int)) and isinstance(b, (float,int)):
        if not np.isclose(a,b,rtol=0,atol=1e-5): mismatches.append(f'{path}: {a} != {b}')
    elif a != b: mismatches.append(f'{path}: {a} != {b}')
    return mismatches


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--gpu',type=int,default=7)
    p.add_argument('--shader',choices=['rt','default'],default='rt')
    p.add_argument('--spp',type=int,default=8)
    p.add_argument('--cameras',default='cam_high,cam_left_wrist,cam_right_wrist')
    p.add_argument('--validate-only',action='store_true')
    p.add_argument('--render-run',type=Path,help='Render a previously validated pose cache in the same reconstructed scene')
    a=p.parse_args(); source=a.source.resolve(); output=a.output.resolve()
    output.mkdir(parents=True,exist_ok=False)
    report=read(source/'report.json'); trace,actions,recovered=actions_from_source(source,report)
    sys.path[:0]=[str(EVALUATOR/'common'),str(REPO)]
    import controller
    assert report['controller_sha256']==hashlib.sha256((EVALUATOR/'common/controller.py').read_bytes()).hexdigest()
    for path,digest in report.get('runtime_sources',{}).items():
        f=Path(path)
        assert f.is_file() and hashlib.sha256(f.read_bytes()).hexdigest()==digest, f'Changed source: {f}'
    import sapien
    pci=subprocess.check_output(['nvidia-smi','--id='+str(a.gpu),'--query-gpu=pci.bus_id','--format=csv,noheader'],text=True).strip().lower()[-12:]
    def create(engine,config=None):
        if config is not None: sapien.physx.set_scene_config(config)
        return sapien.Scene([sapien.physx.PhysxCpuSystem(),sapien.render.RenderSystem('pci:'+pci)])
    sapien.Engine.create_scene=create
    # The original low-resolution cameras remain RT 32 spp; use OptiX where
    # task code requests OIDN, avoiding the known OIDN GPU device-loss issue.
    native_denoiser=sapien.render.set_ray_tracing_denoiser
    sapien.render.set_ray_tracing_denoiser=lambda name:native_denoiser('optix' if name=='oidn' else name)
    from deployment.model_server.tools import websocket_policy_client
    class SavedActionsClient:
        def __init__(self,*args,**kwargs): self.index=0
        def get_server_metadata(self):
            return dict(action_chunk_size=1,preserve_image_resolution=True,requires_state=True,
                        ckpt_path='saved-action-trace-replay-no-inference')
        def predict_action(self,*args,**kwargs):
            assert self.index < len(actions), 'Evaluator requested an action beyond the saved rollout'
            target=np.asarray(actions[self.index]);self.index+=1
            wire=target[[0,1,2,3,4,5,7,8,9,10,11,12,6,13]]
            return {'data':{'actions':wire[None,None,:]}}
        def close(self): pass
    websocket_policy_client.WebsocketClientPolicy=SavedActionsClient
    recording=SceneRecording(output,output)
    class SceneReady(BaseException): pass
    scene_ready=False
    native_action=controller.take_action_30hz
    native_scene_step=sapien.Scene.step
    def step(scene):
        result=native_scene_step(scene)
        if recording.env is not None and recording.env.scene is scene: recording.steps+=1
        return result
    sapien.Scene.step=step
    def action(env,target,action_type='qpos'):
        nonlocal scene_ready
        if recording.env is None:
            recording.start(env)
            # Retain the scene for offline rendering after official reporting.
            env.close_env=lambda *args,**kwargs:None
            env.release_episode_resources=lambda *args,**kwargs:None
            recording.capture()
            if a.render_run:
                scene_ready=True
                raise SceneReady()
        try: return native_action(env,target,action_type)
        finally: recording.capture()
    controller.take_action_30hz=action
    started=time.monotonic()
    dump(output/'source.json',dict(source_episode=str(source),task=report['task'],episode_index=report['episode_index'],
         recovered_actions=recovered,source_report_sha256=hashlib.sha256((source/'report.json').read_bytes()).hexdigest(),
         source_action_trace_sha256=hashlib.sha256((source/'action_trace.jsonl').read_bytes()).hexdigest()))
    official_output=output/'official_replay'
    sys.argv=[str(EVALUATOR/'run_eval.py'),'--task',report['task'],'--episode-index',str(report['episode_index']),
              '--output',str(official_output),'--steps',str(report['action_budget'])]
    try: runpy.run_path(str(EVALUATOR/'run_eval.py'),run_name='__main__')
    except (SystemExit,SceneReady) as exc:
        if not scene_ready and (not isinstance(exc,SystemExit) or exc.code not in (0,None)): raise
    if a.render_run:
        assert scene_ready
        cached=a.render_run.resolve()
        validation=read(cached/'validation.json')
        assert validation['passed']
        assert read(cached/'source.json')['source_action_trace_sha256']==read(output/'source.json')['source_action_trace_sha256']
        with gzip.open(cached/'scene_poses.pkl.gz','rb') as f:saved=pickle.load(f)
        assert [e.name for e in recording.entities]==[e['name'] for e in saved['entities']], 'Scene entities differ'
        assert recording.camera_info==saved['camera_info'], 'Scene cameras differ'
        recording.frames=saved['frames'];recording.reference=saved['references']
        recording.steps=read(cached/'capture.json')['physics_steps']
        recording.active=False
        for name in ['report.json','action_trace.jsonl','episode.mp4']:
            shutil.copy2(cached/'official_replay'/name,official_output/name)
        dump(output/'validation.json',dict(validation,pose_cache_source=str(cached)))
        recording.stop()
        recording.frames.extend([recording.frames[-1]]*30)
        videos=recording.render(spp=a.spp,shader=a.shader,path_depth=4,camera_names=a.cameras.split(','))
        dump(output/'result.json',dict(task=report['task'],episode_index=report['episode_index'],
             source_success=report['policy_success'],source_steps=report['steps'],videos=videos,
             validation=validation,pose_cache_source=str(cached),terminal_hold_frames=30,
             render_denoiser='optix' if a.shader=='rt' else None,complete=True))
        return
    actual=read(official_output/'report.json')
    actual_trace=[json.loads(s) for s in (official_output/'action_trace.jsonl').read_text().splitlines() if s]
    assert len(actual_trace)==len(trace), f'Trace length mismatch {len(actual_trace)} != {len(trace)}'
    max_error=0.
    for old,new in zip(trace,actual_trace):
        assert old['action_index']==new['action_index'] and old['physics_steps']==new['physics_steps']
        assert np.array_equal(old['target'],new['target'])
        max_error=max(max_error,float(np.max(np.abs(np.asarray(old['observed_joint_state'])-new['observed_joint_state']))))
    mismatches=[]
    for k in ['ok','steps','seed','policy_success','termination_reason','controller_physics_steps','final_task_state','fail_reason',
              'scene_spec','parameters','source_scene_table','source_scene_manifest','scene_manifest_source','scene_mapping_source']:
        if k in report: compare_values(report[k],actual.get(k),k,mismatches)
    validation=dict(actions=len(actions),logged_actions=len(trace),recovered_terminal_actions=len(recovered),
         max_observed_joint_error=max_error,tolerance=1e-5,report_mismatches=mismatches,
         passed=max_error<=1e-5 and not mismatches,source_success=report['policy_success'],replay_success=actual['policy_success'],
         source_steps=report['steps'],replay_steps=actual['steps'],collection_seconds=time.monotonic()-started)
    dump(output/'validation.json',validation)
    recording.stop()
    assert validation['passed'], f'Replay mismatch: {validation}'
    print('ACTION_REPLAY_VERIFIED',validation,flush=True)
    if a.validate_only: return
    # One second held terminal image at 30 fps, without advancing physics.
    recording.frames.extend([recording.frames[-1]]*30)
    videos=recording.render(spp=a.spp,shader=a.shader,path_depth=4,camera_names=a.cameras.split(','))
    dump(output/'result.json',dict(task=report['task'],episode_index=report['episode_index'],
         source_success=report['policy_success'],source_steps=report['steps'],videos=videos,
         validation=validation,terminal_hold_frames=30,render_denoiser='optix' if a.shader=='rt' else None,complete=True))


if __name__=='__main__':
    main()
    # All writers have closed and verification/metadata have committed. SAPIEN
    # can segfault during Python's unordered C++ destructor shutdown after
    # pose restoration; release the isolated process through the OS instead.
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0)
