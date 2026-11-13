"""Run each selected trajectory in an isolated simulator process; resume safely."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from scene_recording import dump


def environment(gpu):
    env=os.environ.copy()
    env.update(PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',CUDA_VISIBLE_DEVICES=str(gpu),
        OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1',
        XDG_RUNTIME_DIR='/tmp',VK_ICD_FILENAMES='/etc/vulkan/icd.d/nvidia_icd.json',
        LD_LIBRARY_PATH=str(Path(sys.executable).parent.parent/'lib')+':/usr/lib/x86_64-linux-gnu')
    for family in ['OD1','OD2','PD1','PD2','SD1','SD2']:env[family+'_PHYSICAL_GPU']=str(gpu)
    for key in ['__EGL_VENDOR_LIBRARY_FILENAMES','__EGL_VENDOR_LIBRARY_DIRS']:env.pop(key,None)
    return env


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--selected',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--gpu',type=int,default=7)
    p.add_argument('--shader',default='rt',choices=['rt','default'])
    p.add_argument('--only',default='')
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    jobs=sorted(a.selected.rglob('report.json'))
    status=[]
    for report in jobs:
        relative=report.relative_to(a.selected)
        task,round_name=relative.parts[:2]
        if a.only and task not in a.only.split(','):continue
        target=a.output/task/round_name
        if (target/'result.json').exists():
            status.append(dict(task=task,round=round_name,status='complete'));continue
        extra=[]
        if target.exists():
            validated=target/'validation.json'
            if validated.exists() and json.loads(validated.read_text())['passed'] and (target/'scene_poses.pkl.gz').exists():
                cache=target.with_name(round_name+'.cache_'+str(time.time_ns()))
                target.rename(cache)
                extra=['--render-run',str(cache)]
            else:
                status.append(dict(task=task,round=round_name,status='existing_incomplete'));continue
        target.parent.mkdir(parents=True,exist_ok=True)
        print('START',task,round_name,flush=True)
        with (target.parent/(round_name+'.log')).open('w') as log:
            proc=subprocess.run([sys.executable,'-B',str(Path(__file__).with_name('replay.py')),
                 '--source',str(report.parent),'--output',str(target),'--gpu',str(a.gpu),'--shader',a.shader,*extra],
                 env=environment(a.gpu),stdout=log,stderr=subprocess.STDOUT)
        good=proc.returncode==0 and (target/'result.json').exists()
        status.append(dict(task=task,round=round_name,status='complete' if good else 'failed',returncode=proc.returncode))
        dump(a.output/'batch_status.json',status)
        print('FINISH',status[-1],flush=True)
    dump(a.output/'batch_status.json',status)
    if any(s['status']!='complete' for s in status):raise SystemExit(1)


if __name__=='__main__':main()
