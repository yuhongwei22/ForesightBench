"""Record replayed scene poses and render them natively at 2880x2160.

All controller inputs, physics clocks, and source files stay native. Only the
offline recording camera uses the larger image size. No video upscaling.
"""
import argparse
import fcntl
import gzip
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import pickle
import runpy
import subprocess
import sys
import time
import traceback

WORKSPACE = Path('/cpfs01/zijian.pan/domino_workspace')
OUTPUT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT, FPS = 2880, 2160, 30
CAMERAS = ('cam_high', 'cam_left_wrist', 'cam_right_wrist')


def dump(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2,
                              default=lambda x: x.tolist() if hasattr(x, 'tolist') else str(x)) + '\n')
    tmp.replace(path)


def read(path):
    return json.loads(Path(path).read_text())


def load(path, name):
    sys.path.insert(0, str(Path(path).parent))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class SceneRecording:
    def __init__(self, run, destination):
        self.run, self.destination = run, destination
        self.env = None
        self.steps = 0
        self.frames = []
        self.visuals = {}
        self.entities = []
        self.entity_indices = {}
        self.last_poses = {}
        self.last_visibility = {}
        self.reference = {}
        self.active = False

    def start(self, env):
        if self.env is not None:
            assert self.env is env
            return
        self.env = env
        self.dt = float(env.scene.get_timestep())
        self.sources = dict(zip(CAMERAS, [
            env.cameras.static_camera_list[env.cameras.head_camera_id],
            env.cameras.left_camera, env.cameras.right_camera]))
        self.camera_info = {name: dict(width=cam.get_width(), height=cam.get_height(),
            intrinsic=cam.get_intrinsic_matrix().tolist(), near=cam.near, far=cam.far)
            for name, cam in self.sources.items()}
        self.active = True
        print('CAPTURE_START', self.dt, self.camera_info, flush=True)

    def before_step(self, scene):
        if not self.active or scene is not self.env.scene:
            return
        if self.steps * self.dt + 1e-10 >= len(self.frames) / FPS:
            self.capture()

    def capture(self):
        import numpy as np
        import sapien
        self.env._update_render()
        visibility = {}
        entity_keys, poses = [], []
        for entity in self.env.scene.entities:
            identity = id(entity)
            if identity not in self.entity_indices:
                self.entity_indices[identity] = len(self.entities)
                self.entities.append(entity)
            key = self.entity_indices[identity]
            entity_keys.append(key)
            pose = entity.get_pose()
            poses.append(np.r_[pose.p, pose.q])
            for component in entity.components:
                if isinstance(component, sapien.render.RenderBodyComponent):
                    visual_key = (key, component.name)
                    self.visuals[visual_key] = component
                    visibility[visual_key] = float(component.visibility)
        self.frames.append((np.asarray(poses, dtype=np.float32).tobytes(), visibility, self.steps * self.dt,
                            str(getattr(self.env, 'phase', getattr(self.env, 'traj_phase', ''))), entity_keys))
        if len(self.frames) - 1 in (0, 30, 120):
            cam = self.sources['cam_high']
            cam.take_picture()
            self.reference[len(self.frames)-1] = np.clip(cam.get_picture('Color')[..., :3]*255, 0, 255).astype('uint8')
        if len(self.frames) % 300 == 0:
            print('CAPTURE_PROGRESS', len(self.frames), self.frames[-1][2], flush=True)

    def stop(self):
        self.active = False
        assert self.frames, 'No scene frames captured'
        with gzip.open(self.run/'scene_poses.pkl.gz', 'wb', compresslevel=3) as f:
            pickle.dump(dict(frames=self.frames, camera_info=self.camera_info,
                             references=self.reference,
                             entities=[dict(key=i, name=e.name) for i,e in enumerate(self.entities)]), f, protocol=5)
        dump(self.run/'capture.json', dict(frames=len(self.frames), fps=FPS,
            physics_dt=self.dt, physics_steps=self.steps, cameras=self.camera_info,
            timing='initial state and after each 30 Hz action; terminal action may contain fewer physics substeps',
            method='native simulation entity poses and render visibility; offline native-resolution rendering'))

    def restore(self, frame, update=True):
        import numpy as np
        import sapien
        # Scene.pack_poses uses positional order; actor removal changes that
        # order. Explicit entity identities also preserve actors removed later.
        for entity in self.entities:
            if entity.scene is None:
                self.env.scene.add_entity(entity)
        poses = np.frombuffer(frame[0], dtype=np.float32).reshape(-1, 7)
        for key, pose in zip(frame[4], poses):
            previous = self.last_poses.get(key)
            if previous is None or not np.array_equal(previous, pose):
                self.entities[key].set_pose(sapien.Pose(pose[:3], pose[3:]))
                self.last_poses[key] = pose
        for key, component in self.visuals.items():
            visibility = frame[1].get(key, 0.)
            if self.last_visibility.get(key) != visibility:
                component.visibility = visibility
                self.last_visibility[key] = visibility
        if update:
            self.env.scene.update_render()

    def verify_replay(self):
        import numpy as np
        from PIL import Image
        # Check pose replay against actual live rendered frames before exporting.
        checks = []
        for index, reference in self.reference.items():
            self.restore(self.frames[index])
            cam = self.sources['cam_high']
            cam.take_picture()
            replay = np.clip(cam.get_picture('Color')[..., :3]*255, 0, 255).astype('uint8')
            mse = float(np.mean((reference.astype(float)-replay.astype(float))**2))
            psnr = 10*math.log10(255**2/max(mse, 1e-12))
            checks.append(dict(frame=index, psnr_db=psnr))
            Image.fromarray(reference).save(self.run/f'live_{index:06d}.png')
            Image.fromarray(replay).save(self.run/f'replay_{index:06d}.png')
            assert psnr > 30, f'Pose replay mismatch: frame {index}, PSNR {psnr}'
        dump(self.run/'pose_replay_verification.json', checks)
        print('POSE_REPLAY_VERIFIED', checks, flush=True)

    def render(self, spp=32, shader='rt', path_depth=8, camera_names=CAMERAS):
        import cv2
        import numpy as np
        import sapien
        from PIL import Image
        self.verify_replay()
        sapien.render.set_ray_tracing_samples_per_pixel(spp)
        sapien.render.set_ray_tracing_path_depth(path_depth)
        sapien.render.set_ray_tracing_denoiser('optix')
        sapien.render.set_camera_shader_dir(shader)
        hd = self.env.scene.add_camera('policy_replay_native_2880x2160', WIDTH, HEIGHT,
                                       math.radians(45), .05, 100)
        self.destination.mkdir(parents=True, exist_ok=True)
        results = []
        for name, source in self.sources.items():
            if name not in camera_names:
                continue
            info = self.camera_info[name]
            K = np.asarray(info['intrinsic'])
            sx, sy = WIDTH/info['width'], HEIGHT/info['height']
            hd.set_perspective_parameters(info['near'], info['far'],
                K[0,0]*sx, K[1,1]*sy, K[0,2]*sx, K[1,2]*sy, K[0,1]*sx)
            temp = self.run/(name+'.rendering.mp4')
            cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin', '-y',
                '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{WIDTH}x{HEIGHT}',
                '-r', str(FPS), '-i', 'pipe:0', '-an', '-c:v', 'libx264',
                '-preset', 'veryfast', '-crf', '18', '-threads', '2',
                '-pix_fmt', 'yuv420p', '-tag:v', 'avc1', '-movflags', '+faststart', str(temp)]
            start = time.monotonic()
            with (self.run/(name+'_ffmpeg.log')).open('w') as log:
                proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=log)
                try:
                    previous_frame = None
                    for index, frame in enumerate(self.frames):
                        if frame is previous_frame:
                            proc.stdin.write(image.tobytes())
                            continue
                        t0 = time.monotonic()
                        self.restore(frame, update=False)
                        hd.entity.set_pose(source.entity.get_pose())
                        self.env.scene.update_render()
                        t1 = time.monotonic()
                        hd.take_picture()
                        t2 = time.monotonic()
                        rgba = hd.get_picture('Color')
                        t3 = time.monotonic()
                        image = cv2.cvtColor(cv2.convertScaleAbs(rgba, alpha=255), cv2.COLOR_RGBA2RGB)
                        t4 = time.monotonic()
                        assert image.shape == (HEIGHT, WIDTH, 3)
                        previous_frame = frame
                        proc.stdin.write(image.tobytes())
                        if index == 2:
                            print('RENDER_TIMING', name, dict(poses=t1-t0, draw=t2-t1,
                                download=t3-t2, convert=t4-t3, encode=time.monotonic()-t4), flush=True)
                        if index == 0:
                            Image.fromarray(image).save(self.run/(name+'_first.png'))
                        if index % 30 == 0:
                            print('RENDER_PROGRESS', name, index+1, len(self.frames),
                                  round(time.monotonic()-start, 1), flush=True)
                    proc.stdin.close()
                    assert proc.wait() == 0, f'ffmpeg failed for {name}'
                finally:
                    if proc.poll() is None:
                        proc.terminate()
                        proc.wait()
            metadata = json.loads(subprocess.check_output(['ffprobe', '-v', 'error',
                '-count_frames', '-show_streams', '-show_format', '-of', 'json', str(temp)], text=True))
            stream = metadata['streams'][0]
            assert (stream['width'], stream['height']) == (WIDTH, HEIGHT)
            assert stream['r_frame_rate'] == '30/1'
            assert int(stream['nb_read_frames']) == len(self.frames)
            final = self.destination/(name+'.mp4')
            temp.replace(final)
            result = dict(file=final.name, camera=name,
                width=WIDTH, height=HEIGHT, fps=FPS, frames=len(self.frames),
                duration_seconds=float(metadata['format']['duration']), codec=stream['codec_name'],
                bytes=final.stat().st_size, sha256=hashlib.sha256(final.read_bytes()).hexdigest(),
                full_decode_verified=True, native_render=True, upscale=False,
                render_shader=shader, render_spp=spp, render_path_depth=path_depth,
                render_seconds=round(time.monotonic()-start, 2))
            results.append(result)
            dump(self.run/'render_progress.json', results)
            print('VIDEO_COMPLETE', result, flush=True)
        return results
