# ForesightBench：面向机器人操作的决策相关物理智能评测

**英文标题（暂定）：ForesightBench: Evaluating Decision-Relevant Physical Intelligence in Robotic Manipulation**

> 中文初稿。首图使用 `foresightbench_overview.png`。实验结论以占位符保留；参数敏感性、决策适应性和证据利用分析为拟议实验，不代表已完成验证。本说明及文末写作备注不进入投稿正文。

## Abstract

通用机器人操作策略已取得显著进展，但现有基准对其物理决策能力的评估仍不充分。许多操作基准主要面向相对静态的场景，对运动目标及其演化过程的考察较为有限。动态操作基准进一步引入运动目标与时序约束，但任务的动态性本身，尚不足以系统检验物理判断如何指导行动。我们关注的核心问题是：机器人能否根据物理世界的状态与变化作出决策，将任务意图转化为有效行动。

本文提出 ForesightBench，一个面向机器人操作的决策相关物理智能评测基准。我们从三种物理信息利用方式刻画这一能力：通过观察运动选择干预位置与时机，通过观察与交互辨识物体属性并作出选择，以及通过推演动作后果确定操作配置与顺序。ForesightBench 围绕运动观察驱动决策（OD）、属性辨识驱动决策（PD）和后果推演驱动决策（SD）三类问题，设置六个任务族、十八个难度设置。我们比较不同模型的闭环任务成功率，并进一步分析模型对物理参数变化的敏感性、对决策变化的适应能力，以及运动、交互和几何信息在决策中的作用。**【待补实验结论：根据正式评测填写主要模型表现及分析发现。】** ForesightBench 旨在为评估机器人将物理判断转化为有效行动的能力，提供可控、可复现的实验基础。

![ForesightBench 任务概览](foresightbench_overview.png)

**图 1. ForesightBench 的任务概览。** 上、中、下三行依次对应三种物理信息利用方式。**Observe for Decision（OD）**：观察小球沿斜坡的运动与单摆的摆动，选择接取位置和切绳时机。**Property for Decision（PD）**：比较推动后的滑动响应或抓取时的夹爪开合，辨识摩擦或尺寸异常并完成分拣。**Simulate for Decision（SD）**：调整斜板的位置与朝向，或配置反弹板，形成使小球到达目标的运动路径。六个任务族各设三个难度，图中展示代表性场景；轨迹、重影和姿态标注用于说明任务中的物理过程与决策变量。

## 1. Introduction

使机器人能够根据人的意图在物理世界中完成任务，是具身智能的核心目标。近年来，视觉—语言—动作模型和通用机器人策略的发展，使机器人能够利用视觉观测与语言指令生成动作，并在多种操作任务中展现出进展 [RT-2][rt2]。随着策略能力与应用范围不断扩展，可靠的评测对于理解模型能够完成什么、如何应对环境变化以及何时失败愈发重要。现有基准已从不同角度推动这一研究：[LIBERO][libero] 研究多任务学习与知识迁移，[RoboTwin 2.0][robotwin] 提供双臂任务与域随机化评测，[RoboCasa365][robocasa365] 和 [BEHAVIOR-1K][behavior1k] 将评测扩展到多样化的日常场景和长时程任务；[LIBERO-Plus][libero-plus] 系统考察输入与环境变化下的鲁棒性，[RoboDojo][robodojo] 则结合仿真与真实世界评测多种操作能力。这些基准为比较通用机器人策略和研究操作泛化提供了重要基础。

与此同时，近期研究正将评测进一步扩展到动态环境和物理推理。[DOMINO][domino] 面向动态操作，研究运动历史与未来状态预测；[RoboDyna][robodyna] 在由物理规律驱动的动态场景中评测操作，并比较同步与异步执行；[IMBench][imbench] 将物理约束理解、动作生成与闭环执行结合起来。物体运动、隐藏属性和行动后果因此已成为机器人评测的重要组成部分。在这些进展之上，我们进一步关注：**机器人能否获取并利用物理世界中与任务有关的信息，帮助自己作出决策并完成任务？**
这一问题源于物理环境中任务意图与具体行动之间的距离。任务指令通常只规定目标，而完成目标所需的决策取决于环境的具体状态与物理过程。机器人需要从运动中获取信息，通过观察与交互辨识物体属性，或结合环境结构判断行动后果，并据此选择有效行动。我们将这一从任务意图到物理行动的过程概括为 **Intent-to-Action**，并将其中获取与利用物理证据、选择和执行有效行动的能力称为**决策相关物理智能（Decision-Relevant Physical Intelligence）**。

然而，最终任务成功并不总能揭示模型如何形成决策。机器人接住小球可能依赖对运动过程的判断，也可能受益于较集中的落点或较大的接取容差；正确分拣异常方块可能来自对推动反馈的利用，也可能借助与标签偶然相关的外观或位置线索。已有基准分析同样提醒我们，单一评测条件下的分数需要结合受控诊断解读 [benchmark-audit][benchmark-audit]。因此，除了比较任务成功率，我们还需要考察不同来源的物理信息是否帮助模型完成任务，以及物理因素变化后模型能否利用这些信息调整行动。

为此，我们提出 **ForesightBench**，一个面向机器人操作的决策相关物理智能评测基准。如图 1 所示，基准在仿真环境中组织了三类问题，共六个任务族、十八个难度设置。**Observe for Decision（OD）** 包含斜坡接球与单摆切绳，关注运动观察如何支持接取位置和干预时机的选择。**Property for Decision（PD）** 包含摩擦异常方块与尺寸异常小球分拣，关注观察与交互获得的属性信息如何支持对象识别和分类。**Simulate for Decision（SD）** 包含斜板进洞与击球进洞，关注环境几何和操作配置如何影响后续运动，以及模型能否选择使球到达目标的行动。不同难度分别引入姿态调整、路径分支、多对象比较或更严格的执行容差等要求。三类任务按主要决策需求组织，允许能力交叉，也不限定模型采用何种内部预测机制。
我们以闭环任务成功率为主指标，系统评测不同机器人策略在各任务与难度设置下的表现。为深入理解模型如何依据物理信息行动，我们进一步从三个层面开展分析：通过改变关键物理参数，刻画模型表现对环境变化的敏感性；通过构造需要不同行动的配对场景，考察模型能否随物理条件变化调整决策；通过分析运动观察、交互反馈以及环境几何与行动后果之间的关系，研究任务相关信息如何支持有效行动。这些分析将物理条件、决策行为与任务结果联系起来，为理解机器人策略的能力与局限提供更细致的依据。

**【待补实验结论段：根据正式评测，概括不同模型在各任务上的主要表现，以及参数变化、决策适应与证据利用分析中的实证发现。】**

本文的主要贡献概括如下：

1. **面向决策的物理智能评测视角。** 围绕 Intent-to-Action，关注机器人如何获取和利用任务相关的物理信息，并将其转化为有效行动。
2. **ForesightBench 任务体系。** 在可控仿真环境中构建运动观察、属性辨识和后果推演三类任务，共六个任务族、十八个难度设置，将物理信息的利用与实际接取、分拣和入洞结果相联系。
3. **结合闭环评测与针对性分析的实验体系。** 比较不同机器人策略的任务表现，并从物理参数敏感性、决策适应性和证据利用三个方面，分析模型如何响应物理变化以及任务相关信息如何影响行动。

## 写作备注（不进入论文正文）

- 当前摘要与贡献列出的是研究框架、任务范围及协议设计。投稿前需逐项核对实现与实验覆盖范围，并据正式结果补齐摘要和引言中的实证发现。
- [RoboDyna][robodyna] 已包含斜坡接球、周期运动和台球等任务，并评测物理动态与执行；[IMBench][imbench] 涵盖动力学、隐藏状态和因果操作。ForesightBench 与这些工作存在实质交集，论文应结合最终实现的场景和实验协议逐项比较，避免仅凭任务类型、闭环执行或证据获取宣称独有性。
- 参数敏感性分析使用训练轨迹对应的初始场景，结果应解释为熟悉场景附近的参数变化表现；未见场景或分布外泛化需要独立的测试设置。
- PD2 的尺寸可能从视觉中直接判断。本稿将其表述为属性辨识，并保留视觉与抓取反馈两种证据来源；是否必须依赖交互，需要相应消融支持。固定顺序的探测也不能直接作为自主探测选择能力的证据。
- SD 中改变板子的初始角度可以分析姿态调整能力；若要分析几何条件与动作后果的关系，还需验证变化后的可行配置确实与原场景不同。
- 本稿将连续物理过程中的行动适应作为研究目标，对模型物理能力及内部机制的判断需由行为与对照证据支持。当前结论范围限定于仿真机器人操作，真实机器人迁移需单独验证。

## 引用来源

以下链接对应正文引用的论文或作者项目页，后续可转换为 BibTeX。

1. [RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control][rt2].
2. [LIBERO: Benchmarking Knowledge Transfer for Lifelong Robot Learning][libero].
3. [RoboTwin 2.0: A Scalable Data Generator and Benchmark with Strong Domain Randomization for Robust Bimanual Robotic Manipulation][robotwin].
4. [RoboCasa365: A Large-Scale Simulation Framework for Training and Benchmarking Generalist Robots][robocasa365].
5. [BEHAVIOR-1K: A Human-Centered, Embodied AI Benchmark with 1,000 Everyday Activities and Realistic Simulation][behavior1k].
6. [LIBERO-Plus: A Progressive Robustness Benchmark for Visual-Language-Action Models][libero-plus].
7. [RoboDojo: A Unified Sim-and-Real Benchmark for Comprehensive Evaluation of Generalist Robot Manipulation Policies][robodojo].
8. [Towards Generalizable Robotic Manipulation in Dynamic Environments（DOMINO / PUMA）][domino].
9. [Benchmarking Robotic Manipulation under Physically Realistic Dynamics（RoboDyna）][robodyna].
10. [IMBench: A Benchmark for Intuitive Robotic Manipulation][imbench].
11. [What Are We Actually Benchmarking in Robot Manipulation?][benchmark-audit].

[rt2]: https://arxiv.org/abs/2307.15818
[libero]: https://arxiv.org/abs/2306.03310
[robotwin]: https://arxiv.org/abs/2506.18088
[robocasa365]: https://arxiv.org/abs/2603.04356
[behavior1k]: https://arxiv.org/abs/2403.09227
[libero-plus]: https://openaccess.thecvf.com/content/CVPR2026/papers/Fei_LIBERO-Plus_A_Progressive_Robustness_Benchmark_for_Visual-Language-Action_Models_CVPR_2026_paper.pdf
[robodojo]: https://arxiv.org/abs/2607.04434
[domino]: https://arxiv.org/abs/2603.15620
[robodyna]: https://robodyna.github.io/robodyna/
[imbench]: https://arxiv.org/abs/2607.15641
[benchmark-audit]: https://arxiv.org/abs/2606.04233
