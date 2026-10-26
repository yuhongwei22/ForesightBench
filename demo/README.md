# ForesightBench 演示视频

6 个任务 × 3 个难度，每条轨迹包含 3 个同步视角，共 18 条轨迹、54 条视频。OD1 medium 采用小球走下层斜板并向左落下的成功样例。

目录为 `任务/难度/`，每个目录包含 `cam_high.mp4`（主视角）、`cam_left_wrist.mp4`（左腕）、`cam_right_wrist.mp4`（右腕）。三个视角均来自同一条轨迹。

视频保留原分辨率、帧率、帧数与完整时长。PD1 的九个演示副本原为 MPEG-4 Part 2（mp4v），已转成 H.264 Baseline、yuv420p、avc1 并启用 faststart，便于 VS Code/浏览器预览；其余视频直接复制。已逐条完整解码、核对数据集帧数并校验 SHA-256。原始训练/测试数据未修改。

优先选测试集；PD1 easy、PD1 hard、PD2 hard 使用已有成功训练轨迹。部分视频来自尚未合并的采集转换目录。

| 任务 | 难度 | 时长 | 来源 | 三个视角 |
|---|---|---|---|---|
| SD1 斜板进洞 | easy | 23.9s | 测试集 | [主视角](SD1/easy/cam_high.mp4) · [左腕](SD1/easy/cam_left_wrist.mp4) · [右腕](SD1/easy/cam_right_wrist.mp4) |
| SD1 斜板进洞 | medium | 30.3s | 测试集 | [主视角](SD1/medium/cam_high.mp4) · [左腕](SD1/medium/cam_left_wrist.mp4) · [右腕](SD1/medium/cam_right_wrist.mp4) |
| SD1 斜板进洞 | hard | 27.3s | 测试集 | [主视角](SD1/hard/cam_high.mp4) · [左腕](SD1/hard/cam_left_wrist.mp4) · [右腕](SD1/hard/cam_right_wrist.mp4) |
| SD2 击球进洞 | easy | 11.5s | 测试集 | [主视角](SD2/easy/cam_high.mp4) · [左腕](SD2/easy/cam_left_wrist.mp4) · [右腕](SD2/easy/cam_right_wrist.mp4) |
| SD2 击球进洞 | medium | 27.8s | 测试集 | [主视角](SD2/medium/cam_high.mp4) · [左腕](SD2/medium/cam_left_wrist.mp4) · [右腕](SD2/medium/cam_right_wrist.mp4) |
| SD2 击球进洞 | hard | 63.9s | 测试集 | [主视角](SD2/hard/cam_high.mp4) · [左腕](SD2/hard/cam_left_wrist.mp4) · [右腕](SD2/hard/cam_right_wrist.mp4) |
| OD1 斜坡接球 | easy | 1.4s | 测试集 | [主视角](OD1/easy/cam_high.mp4) · [左腕](OD1/easy/cam_left_wrist.mp4) · [右腕](OD1/easy/cam_right_wrist.mp4) |
| OD1 斜坡接球 | medium | 2.4s | 测试集 | [主视角](OD1/medium/cam_high.mp4) · [左腕](OD1/medium/cam_left_wrist.mp4) · [右腕](OD1/medium/cam_right_wrist.mp4) |
| OD1 斜坡接球 | hard | 1.4s | 测试集 | [主视角](OD1/hard/cam_high.mp4) · [左腕](OD1/hard/cam_left_wrist.mp4) · [右腕](OD1/hard/cam_right_wrist.mp4) |
| OD2 单摆断绳落球 | easy | 11.9s | 测试集 | [主视角](OD2/easy/cam_high.mp4) · [左腕](OD2/easy/cam_left_wrist.mp4) · [右腕](OD2/easy/cam_right_wrist.mp4) |
| OD2 单摆断绳落球 | medium | 18.1s | 测试集 | [主视角](OD2/medium/cam_high.mp4) · [左腕](OD2/medium/cam_left_wrist.mp4) · [右腕](OD2/medium/cam_right_wrist.mp4) |
| OD2 单摆断绳落球 | hard | 16.1s | 测试集 | [主视角](OD2/hard/cam_high.mp4) · [左腕](OD2/hard/cam_left_wrist.mp4) · [右腕](OD2/hard/cam_right_wrist.mp4) |
| PD1 方块摩擦辨识与分拣 | easy | 26.4s | 训练集 | [主视角](PD1/easy/cam_high.mp4) · [左腕](PD1/easy/cam_left_wrist.mp4) · [右腕](PD1/easy/cam_right_wrist.mp4) |
| PD1 方块摩擦辨识与分拣 | medium | 33.0s | 测试集 | [主视角](PD1/medium/cam_high.mp4) · [左腕](PD1/medium/cam_left_wrist.mp4) · [右腕](PD1/medium/cam_right_wrist.mp4) |
| PD1 方块摩擦辨识与分拣 | hard | 47.2s | 训练集 | [主视角](PD1/hard/cam_high.mp4) · [左腕](PD1/hard/cam_left_wrist.mp4) · [右腕](PD1/hard/cam_right_wrist.mp4) |
| PD2 小球尺寸辨识与分拣 | easy | 84.8s | 测试集 | [主视角](PD2/easy/cam_high.mp4) · [左腕](PD2/easy/cam_left_wrist.mp4) · [右腕](PD2/easy/cam_right_wrist.mp4) |
| PD2 小球尺寸辨识与分拣 | medium | 72.5s | 测试集 | [主视角](PD2/medium/cam_high.mp4) · [左腕](PD2/medium/cam_left_wrist.mp4) · [右腕](PD2/medium/cam_right_wrist.mp4) |
| PD2 小球尺寸辨识与分拣 | hard | 109.3s | 训练集 | [主视角](PD2/hard/cam_high.mp4) · [左腕](PD2/hard/cam_left_wrist.mp4) · [右腕](PD2/hard/cam_right_wrist.mp4) |

每条视频的原始绝对路径、数据集、episode、seed（来源中可用时）、帧数与校验和详见 [manifest.json](manifest.json)。

## OD1 medium：左向分支

`OD1/medium/` 采用小球测试轨迹 seed 5017：经过间隙落到下层绿色斜板，再向左落下并被接住，任务成功。

[主视角](OD1/medium/cam_high.mp4) · [左腕](OD1/medium/cam_left_wrist.mp4) · [右腕](OD1/medium/cam_right_wrist.mp4)

该样例来自 medium 大接球板测试集，路径方向及成功状态已核对 `metrics.json` 与 `collect_status.json`。

PD1 的左腕镜头基本静止并朝向桌外，与原始数据一致；该任务由右臂执行，主视角与右腕视角可观察完整任务过程。
