"""Verify and package the selected policy replay videos for the project repo."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import shutil
import subprocess

from scene_recording import dump, read
from replay import compare_values


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--selected',type=Path,required=True)
    p.add_argument('--runs',type=Path,required=True)
    p.add_argument('--destination',type=Path,required=True)
    a=p.parse_args();a.destination.mkdir(parents=True,exist_ok=True)
    entries=[]
    for source_report in sorted(a.selected.rglob('report.json')):
        relative=source_report.relative_to(a.selected);task,round_name=relative.parts[:2]
        run=a.runs/task/round_name;result=read(run/'result.json');validation=read(run/'validation.json')
        original=read(source_report)
        assert result['complete'] and validation['passed']
        actual=read(run/'official_replay/report.json')
        report_fields=[k for k in ('ok','steps','seed','policy_success','termination_reason',
            'controller_physics_steps','final_task_state','fail_reason','scene_spec','parameters',
            'fixed_v2_runtime_seed','source_scene_table','source_scene_manifest','scene_manifest_source',
            'scene_mapping_source') if k in original]
        for key in report_fields:
            assert not compare_values(original[key],actual.get(key),key), f'Report differs: {task}/{round_name}/{key}'
        assert {v['camera'] for v in result['videos']}=={'cam_high','cam_left_wrist','cam_right_wrist'}
        dest=a.destination/task/round_name;dest.mkdir(parents=True,exist_ok=True)
        frame_counts=set();videos=[]
        for v in result['videos']:
            src=run/(v['camera']+'.mp4')
            assert sha(src)==v['sha256']
            # Decode the entire final bitstream, not only its container header.
            subprocess.run(['ffmpeg','-v','error','-xerror','-threads','2','-i',str(src),'-f','null','-'],check=True)
            meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(src)],text=True))
            stream=meta['streams'][0]
            assert (stream['width'],stream['height'],stream['r_frame_rate'])==(2880,2160,'30/1')
            assert stream['codec_name']=='h264' and stream['pix_fmt']=='yuv420p'
            assert int(stream['nb_frames'])==original['steps']+31
            frame_counts.add(int(stream['nb_frames']))
            shutil.copy2(src,dest/src.name)
            videos.append(dict(v,file=f'{task}/{round_name}/{src.name}',full_decode_verified=True))
        assert len(frame_counts)==1
        shutil.copy2(source_report,dest/'source_report.json')
        shutil.copy2(source_report.with_name('action_trace.jsonl'),dest/'source_action_trace.jsonl')
        for name in ['validation.json','source.json','pose_replay_verification.json']:
            shutil.copy2(run/name,dest/name)
        shutil.copy2(run/'official_replay/report.json',dest/'replay_report.json')
        # Low-resolution replay and source share the original frame schedule.
        import cv2
        source_video=source_report.with_name('episode.mp4')
        x=cv2.VideoCapture(str(source_video));y=cv2.VideoCapture(str(run/'official_replay/episode.mp4'))
        errors=[]
        while True:
            ok1,im1=x.read();ok2,im2=y.read()
            assert ok1==ok2, f'Original video frame count differs: {task}/{round_name}'
            if not ok1:break
            assert im1.shape==im2.shape
            errors.append(float(cv2.absdiff(im1,im2).mean()))
        x.release();y.release()
        assert errors
        visual=dict(compared_frames=len(errors),mean_absolute_rgb_error=sum(errors)/len(errors),
                    maximum_frame_mean_absolute_rgb_error=max(errors),scale='0..255',
                    note='Diagnostic only: original OIDN and replay OptiX denoising can differ.')
        dump(dest/'original_video_comparison.json',visual)
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(dest/'cam_high.mp4'),'-frames:v','1',
                        '-vf','scale=720:540','-q:v','2',str(dest/'preview.jpg')],check=True)
        entry=dict(task=task,round=round_name,episode_index=original['episode_index'],seed=original.get('seed'),
                   fixed_runtime_seed=original.get('fixed_v2_runtime_seed'),source_success=original['policy_success'],
                   termination_reason=original['termination_reason'],steps=original['steps'],videos=videos,
                   validation=validation,original_video_comparison=visual,
                   verified_report_fields=report_fields,
                   source_report_sha256=sha(source_report),source_trace_sha256=sha(source_report.with_name('action_trace.jsonl')))
        entries.append(entry)
        print('PACKAGED',task,round_name,visual,flush=True)
    assert len(entries)==16 and len({e['task'] for e in entries})==12
    manifest=dict(episodes=entries,episode_count=16,task_count=12,video_count=48,width=2880,height=2160,fps=30,
                  native_render=True,upscale=False,inference_calls=0,terminal_hold_frames=30,
                  shader='rt',samples_per_pixel=8,path_depth=4,denoiser='optix',
                  verified=True,total_bytes=sum(v['bytes'] for e in entries for v in e['videos']))
    dump(a.destination/'manifest.json',manifest)
    tools=a.destination/'tools';tools.mkdir(exist_ok=True)
    for src in Path(__file__).parent.glob('*.py'):shutil.copy2(src,tools/src.name)
    lines=['# RoboICL + GPT-6 Astra：原轨迹高清回放','',
      '已完成 **12 个 task、16 条筛选轨迹、48 个视频**。所有视频为原生 **2880×2160、30 fps、4:3**，包含主视角、左腕和右腕。', '',
      '使用原始测试 case（`episode-index 0`）、相同的官方 30 Hz 控制器和已执行的关节动作重放。没有重新调用模型，没有重新采集专家演示，也没有放大低清视频。保留原本的成功和失败结果。', '',
      '逐步核对动作目标、实际关节状态、物理步数和最终任务状态；各条回放均通过核对。之后记录场景位姿与可见性，以独立高清相机离线渲染，保留原相机的内参、姿态和完整视野。末尾额外显示终态 1 秒。', '',
      '渲染使用 RT、8 samples/pixel、path depth 4、OptiX 降噪；原始低清观察使用的 OIDN 降噪在回放中换成 OptiX，因此光照与降噪细节可能略有变化。相机近裁剪面沿用原配置。H.264 / CRF 18 / yuv420p / faststart；48 个最终文件均已完整解码验证。', '',
      'SD2_easy 的第 171 次动作在碰撞异常中终止，原 action trace 只有 170 条；末条动作从该次运行保存的模型决策中恢复，并复现同一碰撞终止原因。恢复依据见该目录的 `source.json`。', '',
      '可下载本目录后打开 [视频浏览页](index.html)。', '',
      '| Task | Round | 原结果 | 动作数 | 三个视角 |','|---|---|---|---:|---|']
    cards=[]
    for e in entries:
        rel=f"{e['task']}/{e['round']}";outcome='成功' if e['source_success'] else '失败'
        links=' · '.join(f'[{label}]({rel}/{cam}.mp4)' for label,cam in [('主视角','cam_high'),('左腕','cam_left_wrist'),('右腕','cam_right_wrist')])
        lines.append(f"| {e['task']} | {e['round']} | {outcome} | {e['steps']} | {links} |")
        cards.append(f'<article><h2>{html.escape(e["task"])} · {e["round"]} · {outcome}</h2><video controls preload="none" poster="{rel}/preview.jpg" src="{rel}/cam_high.mp4"></video><p>'+ ' · '.join(f'<a href="{rel}/{cam}.mp4">{label}</a>' for label,cam in [('主视角','cam_high'),('左腕','cam_left_wrist'),('右腕','cam_right_wrist')])+'</p></article>')
    lines += ['', '每条目录包含原始报告和动作日志、回放报告、数值核对、低清画面差异诊断及位姿重渲染核对。详细视频元数据和 SHA-256 见 [manifest.json](manifest.json)。', '',
              '`tools/` 保存本次使用的回放、渲染和打包脚本。执行需要原评测器、数据 manifest、SAPIEN 及机器人资产；脚本中的默认路径对应本次实验机器。完整场景位姿缓存保存在本地运行目录，不纳入 Git。', '']
    (a.destination/'README.md').write_text('\n'.join(lines))
    (a.destination/'index.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>RoboICL 高清回放</title><style>body{font:16px system-ui;background:#10151e;color:#e9eef6;margin:32px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:24px}article{background:#1b2330;padding:16px;border-radius:12px}h1{font-size:28px}h2{font-size:18px}video{width:100%;aspect-ratio:4/3;background:#000}a{color:#9dc4ff}</style><h1>RoboICL + GPT-6 Astra 高清回放</h1><p>原轨迹 · 2880×2160 · 30 fps · 12 tasks / 16 trajectories / 48 videos</p><main>'+''.join(cards)+'</main></html>')


if __name__=='__main__':main()
