# RoboICL + GPT-6 Astra：原轨迹高清回放

已完成 **12 个 task、16 条筛选轨迹、48 个视频**。所有视频为原生 **2880×2160、30 fps、4:3**，包含主视角、左腕和右腕。

使用原始测试 case（`episode-index 0`）、相同的官方 30 Hz 控制器和已执行的关节动作重放。没有重新调用模型，没有重新采集专家演示，也没有放大低清视频。保留原本的成功和失败结果。

逐步核对动作目标、实际关节状态、物理步数和最终任务状态；各条回放均通过核对。之后记录场景位姿与可见性，以独立高清相机离线渲染，保留原相机的内参、姿态和完整视野。末尾额外显示终态 1 秒。

渲染使用 RT、8 samples/pixel、path depth 4、OptiX 降噪；原始低清观察使用的 OIDN 降噪在回放中换成 OptiX，因此光照与降噪细节可能略有变化。相机近裁剪面沿用原配置。H.264 / CRF 18 / yuv420p / faststart；48 个最终文件均已完整解码验证。

SD2_easy 的第 171 次动作在碰撞异常中终止，原 action trace 只有 170 条；末条动作从该次运行保存的模型决策中恢复，并复现同一碰撞终止原因。恢复依据见该目录的 `source.json`。

可下载本目录后打开 [视频浏览页](index.html)。

| Task | Round | 原结果 | 动作数 | 三个视角 |
|---|---|---|---:|---|
| OD1_easy | round2 | 成功 | 33 | [主视角](OD1_easy/round2/cam_high.mp4) · [左腕](OD1_easy/round2/cam_left_wrist.mp4) · [右腕](OD1_easy/round2/cam_right_wrist.mp4) |
| OD1_hard | round1 | 失败 | 76 | [主视角](OD1_hard/round1/cam_high.mp4) · [左腕](OD1_hard/round1/cam_left_wrist.mp4) · [右腕](OD1_hard/round1/cam_right_wrist.mp4) |
| OD1_hard | round2 | 失败 | 76 | [主视角](OD1_hard/round2/cam_high.mp4) · [左腕](OD1_hard/round2/cam_left_wrist.mp4) · [右腕](OD1_hard/round2/cam_right_wrist.mp4) |
| OD1_medium | round1 | 失败 | 35 | [主视角](OD1_medium/round1/cam_high.mp4) · [左腕](OD1_medium/round1/cam_left_wrist.mp4) · [右腕](OD1_medium/round1/cam_right_wrist.mp4) |
| OD1_medium | round2 | 失败 | 35 | [主视角](OD1_medium/round2/cam_high.mp4) · [左腕](OD1_medium/round2/cam_left_wrist.mp4) · [右腕](OD1_medium/round2/cam_right_wrist.mp4) |
| OD2_easy | round2 | 成功 | 154 | [主视角](OD2_easy/round2/cam_high.mp4) · [左腕](OD2_easy/round2/cam_left_wrist.mp4) · [右腕](OD2_easy/round2/cam_right_wrist.mp4) |
| OD2_hard | round1 | 失败 | 147 | [主视角](OD2_hard/round1/cam_high.mp4) · [左腕](OD2_hard/round1/cam_left_wrist.mp4) · [右腕](OD2_hard/round1/cam_right_wrist.mp4) |
| OD2_hard | round2 | 失败 | 230 | [主视角](OD2_hard/round2/cam_high.mp4) · [左腕](OD2_hard/round2/cam_left_wrist.mp4) · [右腕](OD2_hard/round2/cam_right_wrist.mp4) |
| OD2_medium | round1 | 失败 | 199 | [主视角](OD2_medium/round1/cam_high.mp4) · [左腕](OD2_medium/round1/cam_left_wrist.mp4) · [右腕](OD2_medium/round1/cam_right_wrist.mp4) |
| OD2_medium | round2 | 失败 | 571 | [主视角](OD2_medium/round2/cam_high.mp4) · [左腕](OD2_medium/round2/cam_left_wrist.mp4) · [右腕](OD2_medium/round2/cam_right_wrist.mp4) |
| PD1_easy | round2 | 成功 | 324 | [主视角](PD1_easy/round2/cam_high.mp4) · [左腕](PD1_easy/round2/cam_left_wrist.mp4) · [右腕](PD1_easy/round2/cam_right_wrist.mp4) |
| PD1_hard | round1 | 失败 | 197 | [主视角](PD1_hard/round1/cam_high.mp4) · [左腕](PD1_hard/round1/cam_left_wrist.mp4) · [右腕](PD1_hard/round1/cam_right_wrist.mp4) |
| PD1_medium | round1 | 失败 | 335 | [主视角](PD1_medium/round1/cam_high.mp4) · [左腕](PD1_medium/round1/cam_left_wrist.mp4) · [右腕](PD1_medium/round1/cam_right_wrist.mp4) |
| PD2_easy | round1 | 成功 | 639 | [主视角](PD2_easy/round1/cam_high.mp4) · [左腕](PD2_easy/round1/cam_left_wrist.mp4) · [右腕](PD2_easy/round1/cam_right_wrist.mp4) |
| SD1_easy | round1 | 成功 | 198 | [主视角](SD1_easy/round1/cam_high.mp4) · [左腕](SD1_easy/round1/cam_left_wrist.mp4) · [右腕](SD1_easy/round1/cam_right_wrist.mp4) |
| SD2_easy | round1 | 失败 | 171 | [主视角](SD2_easy/round1/cam_high.mp4) · [左腕](SD2_easy/round1/cam_left_wrist.mp4) · [右腕](SD2_easy/round1/cam_right_wrist.mp4) |

每条目录包含原始报告和动作日志、回放报告、数值核对、低清画面差异诊断及位姿重渲染核对。详细视频元数据和 SHA-256 见 [manifest.json](manifest.json)。

`tools/` 保存本次使用的回放、渲染和打包脚本。执行需要原评测器、数据 manifest、SAPIEN 及机器人资产；脚本中的默认路径对应本次实验机器。完整场景位姿缓存保存在本地运行目录，不纳入 Git。
