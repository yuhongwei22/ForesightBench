# 模型训练与推理评测指南

更新日期：2026-10-30。英文指令版本：`user_latest_train3_test5_v7`。

流程：**选模型 → 适配数据与动作接口 → 配置训练数据混合 → 训练并保存权重/归一化统计 → 在任务仿真环境中闭环推理 → 调用任务成功判定并汇总成绩。**

当前已完成18个设置、3600条轨迹的英文prompt与详细description更新。模型的数据加载、推理接口及完整闭环评测仍需根据所选模型接入。

v2中的SD2 easy/medium训练集与测试集也已补齐为14维，统一采用`[左臂6关节, 左夹爪, 右臂6关节, 右夹爪]`。

## 1. 数据、视频与指令位置

| 内容 | 路径 |
|---|---|
| 新标注、Parquet、meta、description | `/cpfs01/zijian.pan/data_100_100_v2` |
| 视频来源（只读） | `/cpfs01/zijian.pan/data_100_100` |
| 单设置训练数据 | `/cpfs01/zijian.pan/data_100_100_v2/<设置>/train_data` |
| 单设置测试数据 | `/cpfs01/zijian.pan/data_100_100_v2/<设置>/test_data` |
| 对应视频 | `/cpfs01/zijian.pan/data_100_100/<设置>/<train_data或test_data>/videos` |
| 评测代码归档 | `/cpfs01/zijian.pan/data_100_100_v2/<设置>/评测代码细则` |
| 英文prompt JSON | [task_prompts.json](task_prompts.json) |
| 英文prompt表 | [prompt_table.md](prompt_table.md) |
| 中文prompt对照 | [prompt_table.md](/cpfs01/zijian.pan/benchmark_setup_20261028_cn/prompt_table.md) |
| 逐轨迹固定语言分配表 | [prompt_assignments_train3_test5_v7.json](/cpfs01/zijian.pan/prompt_assignments_train3_test5_v7.json) |
| 含完整英文description的任务模板 | [task_instruction](/cpfs01/zijian.pan/data_100_100_v2/description/task_instruction) |
| 详细成功判定与质量分说明 | [scoring_alignment.md](scoring_alignment.md) |
| v2改写验证记录 | [relabel_manifest.json](/cpfs01/zijian.pan/data_100_100_v2/relabel_manifest.json) |
| SD2补齐规则与验证记录 | [SD2_14D_README.md](/cpfs01/zijian.pan/data_100_100_v2/SD2_14D_README.md)、[sd2_14d_manifest.json](/cpfs01/zijian.pan/data_100_100_v2/sd2_14d_manifest.json) |
| 当前评测语言接入及修改记录 | [EVAL_PROMPT_README.md](/cpfs01/zijian.pan/data_100_100_v2/EVAL_PROMPT_README.md) |

每个设置100条训练轨迹、100条测试轨迹，共1800条训练和1800条测试轨迹，记录帧率30Hz。

| 设置 | 训练数据（v2） | 测试数据（v2） | 训练视频（原目录） | 测试视频（原目录） | 评测归档（v2） |
|---|---|---|---|---|---|
| `SD1_easy` | [train_data](/cpfs01/zijian.pan/data_100_100_v2/SD1_easy/train_data) | [test_data](/cpfs01/zijian.pan/data_100_100_v2/SD1_easy/test_data) | [训练视频](/cpfs01/zijian.pan/data_100_100/SD1_easy/train_data/videos) | [测试视频](/cpfs01/zijian.pan/data_100_100/SD1_easy/test_data/videos) | [评测代码](/cpfs01/zijian.pan/data_100_100_v2/SD1_easy/评测代码细则) |
| `SD1_medium` | [train_data](/cpfs01/zijian.pan/data_100_100_v2/SD1_medium/train_data) | [test_data](/cpfs01/zijian.pan/data_100_100_v2/SD1_medium/test_data) | [训练视频](/cpfs01/zijian.pan/data_100_100/SD1_medium/train_data/videos) | [测试视频](/cpfs01/zijian.pan/data_100_100/SD1_medium/test_data/videos) | [评测代码](/cpfs01/zijian.pan/data_100_100_v2/SD1_medium/评测代码细则) |
| `SD1_hard` | [train_data](/cpfs01/zijian.pan/data_100_100_v2/SD1_hard/train_data) | [test_data](/cpfs01/zijian.pan/data_100_100_v2/SD1_hard/test_data) | [训练视频](/cpfs01/zijian.pan/data_100_100/SD1_hard/train_data/videos) | [测试视频](/cpfs01/zijian.pan/data_100_100/SD1_hard/test_data/videos) | [评测代码](/cpfs01/zijian.pan/data_100_100_v2/SD1_hard/评测代码细则) |
| `SD2_easy` | [train_data](/cpfs01/zijian.pan/data_100_100_v2/SD2_easy/train_data) | [test_data](/cpfs01/zijian.pan/data_100_100_v2/SD2_easy/test_data) | [训练视频](/cpfs01/zijian.pan/data_100_100/SD2_easy/train_data/videos) | [测试视频](/cpfs01/zijian.pan/data_100_100/SD2_easy/test_data/videos) | [评测代码](/cpfs01/zijian.pan/data_100_100_v2/SD2_easy/评测代码细则) |
| `SD2_medium` | [train_data](/cpfs01/zijian.pan/data_100_100_v2/SD2_medium/train_data) | [test_data](/cpfs01/zijian.pan/data_100_100_v2/SD2_medium/test_data) | [训练视频](/cpfs01/zijian.pan/data_100_100/SD2_medium/train_data/videos) | [测试视频](/cpfs01/zijian.pan/data_100_100/SD2_medium/test_data/videos) | [评测代码](/cpfs01/zijian.pan/data_100_100_v2/SD2_medium/评测代码细则) |
| `SD2_hard` | [train_data](/cpfs01/zijian.pan/data_100_100_v2/SD2_hard/train_data) | [test_data](/cpfs01/zijian.pan/data_100_100_v2/SD2_hard/test_data) | [训练视频](/cpfs01/zijian.pan/data_100_100/SD2_hard/train_data/videos) | [测试视频](/cpfs01/zijian.pan/data_100_100/SD2_hard/test_data/videos) | [评测代码](/cpfs01/zijian.pan/data_100_100_v2/SD2_hard/评测代码细则) |
| `OD1_easy` | [train_data](/cpfs01/zijian.pan/data_100_100_v2/OD1_easy/train_data) | [test_data](/cpfs01/zijian.pan/data_100_100_v2/OD1_easy/test_data) | [训练视频](/cpfs01/zijian.pan/data_100_100/OD1_easy/train_data/videos) | [测试视频](/cpfs01/zijian.pan/data_100_100/OD1_easy/test_data/videos) | [评测代码](/cpfs01/zijian.pan/data_100_100_v2/OD1_easy/评测代码细则) |
| `OD1_medium` | [train_data](/cpfs01/zijian.pan/data_100_100_v2/OD1_medium/train_data) | [test_data](/cpfs01/zijian.pan/data_100_100_v2/OD1_medium/test_data) | [训练视频](/cpfs01/zijian.pan/data_100_100/OD1_medium/train_data/videos) | [测试视频](/cpfs01/zijian.pan/data_100_100/OD1_medium/test_data/videos) | [评测代码](/cpfs01/zijian.pan/data_100_100_v2/OD1_medium/评测代码细则) |
| `OD1_hard` | [train_data](/cpfs01/zijian.pan/data_100_100_v2/OD1_hard/train_data) | [test_data](/cpfs01/zijian.pan/data_100_100_v2/OD1_hard/test_data) | [训练视频](/cpfs01/zijian.pan/data_100_100/OD1_hard/train_data/videos) | [测试视频](/cpfs01/zijian.pan/data_100_100/OD1_hard/test_data/videos) | [评测代码](/cpfs01/zijian.pan/data_100_100_v2/OD1_hard/评测代码细则) |
| `OD2_easy` | [train_data](/cpfs01/zijian.pan/data_100_100_v2/OD2_easy/train_data) | [test_data](/cpfs01/zijian.pan/data_100_100_v2/OD2_easy/test_data) | [训练视频](/cpfs01/zijian.pan/data_100_100/OD2_easy/train_data/videos) | [测试视频](/cpfs01/zijian.pan/data_100_100/OD2_easy/test_data/videos) | [评测代码](/cpfs01/zijian.pan/data_100_100_v2/OD2_easy/评测代码细则) |
| `OD2_medium` | [train_data](/cpfs01/zijian.pan/data_100_100_v2/OD2_medium/train_data) | [test_data](/cpfs01/zijian.pan/data_100_100_v2/OD2_medium/test_data) | [训练视频](/cpfs01/zijian.pan/data_100_100/OD2_medium/train_data/videos) | [测试视频](/cpfs01/zijian.pan/data_100_100/OD2_medium/test_data/videos) | [评测代码](/cpfs01/zijian.pan/data_100_100_v2/OD2_medium/评测代码细则) |
| `OD2_hard` | [train_data](/cpfs01/zijian.pan/data_100_100_v2/OD2_hard/train_data) | [test_data](/cpfs01/zijian.pan/data_100_100_v2/OD2_hard/test_data) | [训练视频](/cpfs01/zijian.pan/data_100_100/OD2_hard/train_data/videos) | [测试视频](/cpfs01/zijian.pan/data_100_100/OD2_hard/test_data/videos) | [评测代码](/cpfs01/zijian.pan/data_100_100_v2/OD2_hard/评测代码细则) |
| `PD1_easy` | [train_data](/cpfs01/zijian.pan/data_100_100_v2/PD1_easy/train_data) | [test_data](/cpfs01/zijian.pan/data_100_100_v2/PD1_easy/test_data) | [训练视频](/cpfs01/zijian.pan/data_100_100/PD1_easy/train_data/videos) | [测试视频](/cpfs01/zijian.pan/data_100_100/PD1_easy/test_data/videos) | [评测代码](/cpfs01/zijian.pan/data_100_100_v2/PD1_easy/评测代码细则) |
| `PD1_medium` | [train_data](/cpfs01/zijian.pan/data_100_100_v2/PD1_medium/train_data) | [test_data](/cpfs01/zijian.pan/data_100_100_v2/PD1_medium/test_data) | [训练视频](/cpfs01/zijian.pan/data_100_100/PD1_medium/train_data/videos) | [测试视频](/cpfs01/zijian.pan/data_100_100/PD1_medium/test_data/videos) | [评测代码](/cpfs01/zijian.pan/data_100_100_v2/PD1_medium/评测代码细则) |
| `PD1_hard` | [train_data](/cpfs01/zijian.pan/data_100_100_v2/PD1_hard/train_data) | [test_data](/cpfs01/zijian.pan/data_100_100_v2/PD1_hard/test_data) | [训练视频](/cpfs01/zijian.pan/data_100_100/PD1_hard/train_data/videos) | [测试视频](/cpfs01/zijian.pan/data_100_100/PD1_hard/test_data/videos) | [评测代码](/cpfs01/zijian.pan/data_100_100_v2/PD1_hard/评测代码细则) |
| `PD2_easy` | [train_data](/cpfs01/zijian.pan/data_100_100_v2/PD2_easy/train_data) | [test_data](/cpfs01/zijian.pan/data_100_100_v2/PD2_easy/test_data) | [训练视频](/cpfs01/zijian.pan/data_100_100/PD2_easy/train_data/videos) | [测试视频](/cpfs01/zijian.pan/data_100_100/PD2_easy/test_data/videos) | [评测代码](/cpfs01/zijian.pan/data_100_100_v2/PD2_easy/评测代码细则) |
| `PD2_medium` | [train_data](/cpfs01/zijian.pan/data_100_100_v2/PD2_medium/train_data) | [test_data](/cpfs01/zijian.pan/data_100_100_v2/PD2_medium/test_data) | [训练视频](/cpfs01/zijian.pan/data_100_100/PD2_medium/train_data/videos) | [测试视频](/cpfs01/zijian.pan/data_100_100/PD2_medium/test_data/videos) | [评测代码](/cpfs01/zijian.pan/data_100_100_v2/PD2_medium/评测代码细则) |
| `PD2_hard` | [train_data](/cpfs01/zijian.pan/data_100_100_v2/PD2_hard/train_data) | [test_data](/cpfs01/zijian.pan/data_100_100_v2/PD2_hard/test_data) | [训练视频](/cpfs01/zijian.pan/data_100_100/PD2_hard/train_data/videos) | [测试视频](/cpfs01/zijian.pan/data_100_100/PD2_hard/test_data/videos) | [评测代码](/cpfs01/zijian.pan/data_100_100_v2/PD2_hard/评测代码细则) |

### 读取v2数据，配对原目录视频

v2不含视频。任务、split、episode编号、帧顺序和相机键与原目录保持对应。加载器应分别设置数据根目录和视频根目录：

```python
import json
from pathlib import Path

task_id, split_dir = 'SD1_easy', 'train_data'
data_root = Path('/cpfs01/zijian.pan/data_100_100_v2') / task_id / split_dir
video_root = Path('/cpfs01/zijian.pan/data_100_100') / task_id / split_dir
info = json.loads((data_root / 'meta/info.json').read_text())
args = dict(episode_index=0, episode_chunk=0)
parquet_path = data_root / info['data_path'].format(**args)
video_path = video_root / info['video_path'].format(
    **args, video_key='observation.images.cam_high'
)
assert parquet_path.is_file() and video_path.is_file()
```

这是加载器需要实现的路径解析规则。其他episode的`episode_chunk`按`episode_index // info['chunks_size']`计算，相机键从实际`info.json`读取。`video_storage.source_dataset`记录视频来源，但模型读取器需显式使用它；当前没有建立视频链接。不要把整个数据根目录改回原目录，否则会读到旧语言标注。

## 2. prompt如何进入模型

**正式训推均输入英文短prompt；中文表用于核对。前三句用于训练，全部五句用于测试。**

| prompt编号 | 训练 | 测试 | 语言组 |
|---|---|---|---|
| 1、2、3 | 使用 | 使用 | `seen` |
| 4、5 | 不使用 | 使用 | `unseen` |

v2已固定分配：每条训练轨迹使用前三句中的一句，每条测试轨迹使用五句中的一句，同一轨迹所有帧一致。不同轨迹可以相同，也可以不同；无需每次取样或每个epoch重新随机。

训练加载链路：

```text
v2 Parquet的task_index → 同一split的meta/tasks.jsonl中对应的task → 模型分词器
```

`meta/episodes.jsonl`中的`tasks`、`task_description`也已同步。正常读取上述索引的模型可直接获得新指令，无需再做语言覆盖。适配时抽查实际送入分词器的文本，确认没有退回旧指令或固定只取第1句。

长说明保存在`meta/task_description.json`、任务根目录`task_description.json`和episode的`full_description`中，用于理解场景、目标与完成判据，**不追加到模型短prompt**。`prompt_version`、`description_version`是标注版本追踪字段，不是模型输入。

## 3. 选定模型后的训练步骤

1. **确定训练范围与基础权重。** 可以每个设置单独训练，也可以多任务联合训练；对比实验固定训练范围、预算和数据采样权重。
2. **适配数据读取。** 按模型格式配置相机、图像尺寸、state、动作序列长度和英文语言字段，接好v2数据与原目录视频。若模型需要RLDS/HDF5等格式，另存派生数据并保留源任务、split、episode和帧的映射。
3. **适配动作约定。** 明确关节/末端动作、绝对量/增量、左右臂顺序、夹爪含义、归一化和动作执行周期。v2的SD2 easy/medium已将`observation.state`和`action`从7维补齐为14维：前7维固定为该轨迹记录的静止左臂参考值`[0,0,0,0,0,0,1]`，后7维保留原右臂数据。左臂state是按参考值重建，并非恢复的逐帧实测值。14维执行器按同样顺序接收；若接原7维右臂接口，取反归一化后的`action[7:14]`，静止左臂沿用环境参考姿态。控制周期与实验规则保持不变。
4. **配置数据混合。** 多任务通常把各设置的`train_data`注册进模型的数据集列表或mixture，按配置采样即可，不必物理拼接Parquet。若必须合并，应重新映射`task_index`到合并词表，避免不同任务的局部索引冲突，并保留源episode映射。100条示范不会因三种prompt变成300条。
5. **检查实际样本后训练。** 核对图像、state/action、时间对齐与分词前英文文本。仅用训练数据拟合归一化统计；需要验证集时从训练部分另划，保留`test_data`用于最终测试。SD2这四份数据的`stats.json`已按各自当前100条轨迹重算；静止维度标准差为0，归一化器需按模型的常量维度规则处理（如分母加epsilon），反归一化后恢复实际参考值。
6. **保存可复现产物。** 保存检查点、归一化统计、模型/数据混合配置、动作映射、代码版本、prompt版本与分配表；推理复用该检查点对应的处理规则。

现有PUMA适配参考：[custom8-domino-puma-data-preparation.md](/cpfs01/shenyq/repo/worldmodel/memory/custom8-domino-puma-data-preparation.md)，仅覆盖其中8个设置，不能视为全部18个设置已接通。

## 4. 最后用什么评测

**最终任务成绩用各任务仿真环境的在线闭环rollout，由该任务的`check_success()`及对应评分模块判断。**

| 评测方式 | 用途 |
|---|---|
| 在保留的专家测试轨迹上计算动作误差/损失 | 可选的离线诊断，观察动作拟合情况 |
| 模型在仿真测试场景中读取当前观测、预测并执行动作 | 正式任务成功率与质量指标 |

测试轨迹用于追溯场景、语言和可选离线比较；在线推理输入是**当前仿真观测与选定英文指令**。专家动作、专家成功记录不能作为模型成绩。

### 闭环评测步骤

1. **准备可运行环境。** 在完整DOMINO/SAPIEN工作区恢复对应任务、机器人、场景assets与依赖，接入模型权重及推理接口；下节列的是代码归档，不是独立安装包。
2. **固定测试场景。** 核对`case_mapping`、`seed_mapping`、`episode_seed_mapping`、`selection`等实际映射，建立“源test episode → 真实场景参数/seed → 评测场景”的对应关系。episode编号0—99不能直接视为仿真seed；归档冻结表也可能有不同数量的场景。
3. **设置测试指令。** 直接读取对应测试轨迹已保存的英文prompt，同一回合保持一致，不再生成或随机选句。轨迹中已有前三句/全部五句的训练测试分配。评测代码仅负责把该文本传给模型，避免旧模板或硬编码覆盖。若从仿真场景启动，需明确对应的源test episode；已有seed映射可用于查找轨迹，无法匹配时不自动生成新指令。
4. **执行策略循环。** 当前图像/state与英文指令 → 模型预测动作或动作块 → 反归一化与动作映射 → 按约定控制周期执行 → 获取新观测。动作块执行步数、最长回合长度等评测参数应固定并记录。
5. **记录成功与评分。** 环境按既有逻辑调用`check_success()`；达到终止条件或超时后保存结果。成功率、框架评分与任务质量指标分别记录。
6. **汇总报告。** 每个设置报告成功率及回合数，同时报告整体、`seen`和`unseen`子组。建议再报告18个设置成功率的宏平均。初始化错误、超时和失败需留记录，不能静默换场景或删掉失败回合。

当前语言预算是每个测试场景执行一次、使用固定五句之一，并非每个场景五句各跑一次。后者100个场景会产生500次执行，属于另一种评测预算。

```text
成功率 SR = 成功的模型执行回合数 / 纳入统计的全部模型执行回合数
```

每回合至少保存：任务/难度、源test episode、真实场景seed/标识、实际英文prompt及编号、`language_group`、成功/失败、终止原因、执行步数与适用评分。当前整体测试含seen与unseen，不能把整体成功率标成纯unseen成绩。

### 测试语言接入示例

```python
import sys
sys.path.insert(0, '/cpfs01/zijian.pan/data_100_100_v2')
from eval_prompt_runtime import load_episode_prompt

# episode_index是当前评测对应的test_data轨迹编号。
record = load_episode_prompt('SD1_easy', episode_index)
text = record['instruction']
TASK_ENV.set_instruction(text)
assert TASK_ENV.get_instruction() == text
# 将text传给模型；一回合内不重新抽取。
```

**评测语言已修正：** OD1归档的`set_instruction()`现已透传所选句子；SD2 medium/hard入口已移除固定`unseen[0]`及旧的left/right文字断言，改读对应轨迹已有prompt。v2现有OD1/OD2/PD1模型启动脚本也会为外部工作区加上语言适配，避免绕回旧prompt；直接运行外部入口时应按[接入说明](/cpfs01/zijian.pan/data_100_100_v2/EVAL_PROMPT_README.md)设置。OD1原有85毫米高度等物理评分规则保持原样。

## 5. 评测代码与成功判定入口

以下相对路径均从`/cpfs01/zijian.pan/data_100_100_v2/<设置>/评测代码细则/`开始。

| 任务族 | 主要执行/成功判断文件 | 评测主程序或脚本 |
|---|---|---|
| SD1三难度 | `评测环境/envs/foresight_sd_single_yellow_eval.py`；`评测环境/envs/sd_catch_success.py`；hard另含`评测环境/envs/foresight_sd_hard_box_eval.py` | `评测环境/script/eval_policy.py` |
| SD2三难度 | `代码快照/任务包/task_code/bank_shot_clearance_v1.py`中的`check_success()`；环境封装在`代码快照/仿真环境/envs/foresight_bank_shot_clearance_right_v1.py` | `代码快照/统一评分/score_sd2.py`是指标后处理；不是模型rollout启动器。模型运行需在完整工作区接环境与策略接口 |
| OD1 easy | `代码快照/OD_task1_easy_训练测试配置/生成代码/task_30hz.py` | 同目录包内`评测/代码/eval_easy.py`、`eval_easy.sh` |
| OD1 medium | `代码快照/OD_task1_medium_大板_训练测试配置/生成代码/task_30hz.py` | 同目录包内`评测/代码/eval_medium.py`、`eval_medium.sh` |
| OD1 hard | `代码快照/OD_task1_v2_训练测试配置/生成代码/task_30hz.py` | 同目录包内`评测/代码/eval_hard.py`、`eval_hard.sh` |
| OD2三难度 | `代码快照/envs/foresight_pendulum_button_easy_v1.py`、`foresight_pendulum_knife_medium_v1.py`、`foresight_pendulum_knife_hard_v1.py`；共用`pendulum_eval_rules.py` | `代码快照/eval_official_easy.sh`、`eval_official_medium.sh`或`eval_official_hard.sh`，各设置选对应脚本 |
| PD1三难度 | `代码快照/envs/foresight_cube_slide_friction_sort_v1.py`及easy/hard对应适配；共用`cube_slide_scoring.py` | `代码快照/script/eval_policy.py`；`代码快照/domino_eval/eval_cube_slide_easy.sh`、`eval_cube_slide.sh`或`eval_cube_slide_hard.sh` |
| PD2三难度 | `代码快照/envs/foresight_gripper_memory_sort_easy_eval_v1.py`、`foresight_gripper_memory_sort_eval_v1.py`、`foresight_gripper_memory_sort_hard_eval_v1.py`；共用`pd2_outcome_scoring.py` | `代码快照/script/eval_policy.py`；仍需在完整环境中配置对应策略与场景 |

二元成功以对应任务环境为准；框架RC/MS及任务质量分按已有评分模块另行汇总。详细规则见[scoring_alignment.md](scoring_alignment.md)，源码清单见[scoring_sources.json](scoring_sources.json)。

评测语言逻辑已完成静态与隔离行为验证，尚未运行真实模型或GPU仿真。完整任务依赖、场景映射和所选模型策略接口仍需接通；先跑通少量场景确认链路，再按固定测试场景和语言分配正式评测。
