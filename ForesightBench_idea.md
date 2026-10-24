# ForesightBench：面向决策相关物理智能的具身 Benchmark

## 1. 核心定位

ForesightBench 的目标不是继续扩充常规 manipulation skill，而是评估一种尚未被系统刻画的能力：

> **Decision-Relevant Physical Intelligence：具身智能体能否从世界的运动、主动交互以及候选动作的未来后果中获取物理知识，并将其用于决策。**

在许多现有任务中，正确动作可由物体类别、语言指令或任务模板直接决定。ForesightBench 则要求：**仅识别场景中“有什么”不足以确定正确动作**。机器人必须理解当前的物理结构，或从时间演化与主动交互中补充物理证据，才能做出可靠决策。

Benchmark 统一为三类互补能力：

1. **Observe for Decision**：观察世界如何运动，从时间变化中提取决策相关的物理信息。
2. **Probe for Decision**：执行具有信息价值的试探动作，从交互反馈中识别隐藏物理属性。
3. **Simulate for Decision**：依据当前物理结构，在行动前推演动作将触发的因果事件链。

三者构成完整链条：

> **Observe → Probe → Simulate → Decide → Act**

三类任务分别强调不同的信息来源：Observe 从自然运动中读出动态信息；Probe 通过主动交互揭示隐藏属性；Simulate 从当前几何、接触、支撑与约束关系中推演尚未发生的事件。最终三者统一到 decision-making，而非孤立的属性识别或视频预测。

---

## 2. Academic English Introduction

> **ForesightBench is a benchmark for decision-relevant physical intelligence in embodied agents.** Unlike conventional manipulation benchmarks, in which the correct action can often be inferred from a static visual observation or a semantic instruction, ForesightBench introduces *physically aliased* scenarios: scenes that appear visually similar yet demand different decisions because of differences in their latent physical states, dynamics, or action-conditioned outcomes.
>
> The benchmark evaluates three complementary capabilities. **Observe for Decision** requires agents to extract decision-relevant physical evidence from temporal observations of how the world evolves. **Probe for Decision** requires agents to perform informative interactions to reveal latent properties that cannot be reliably inferred from vision alone. **Simulate for Decision** requires agents to mentally roll out action-triggered causal events from the current physical structure—for example, whether opening a supporting door will make a leaning cup fall—before committing to an irreversible action.
>
> Together, these tasks test whether an embodied agent can acquire physical evidence from observation and interaction, transform that evidence into action-conditioned predictions, and use those predictions to make effective decisions. ForesightBench therefore shifts embodied evaluation from recognizing *what is currently visible* to understanding *what the physical world implies for what should be done next*.

核心问题：

> **The central question is not merely whether a robot can execute an action, but whether it can acquire and exploit the physical knowledge necessary to decide which action should be executed.**

宣传语：

> **See how the world moves. Probe what cannot be seen. Simulate what actions will cause.**

---

## 3. 与 IMBench 和 RoboDojo 的区别

| Benchmark | 核心评价问题 | 主要信息来源 |
|---|---|---|
| RoboDojo | 机器人能否完成广泛的 manipulation tasks？ | 当前观测、语言指令和策略能力 |
| IMBench | 机器人能否结合物理推理与动作执行，满足操作约束？ | 场景结构、任务约束和执行反馈 |
| ForesightBench | 机器人能否获取并利用决策相关的物理证据，选择具有最佳未来后果的动作？ | 时间运动、主动交互反馈和反事实动作后果 |

ForesightBench 通过 **physical aliasing** 控制任务：初始视觉和语义信息相同或近似，但隐藏物理状态不同，正确决策也不同。只有真正利用动态观察或交互反馈的模型才能解除歧义。

---

## 4. 三类能力与示例任务

### 4.1 Observe for Decision

机器人先观察一段自然运动或环境演化，再依据其中透露的速度、加速度、摩擦、弹性、质量分布等信息决策。关键证据存在于 temporal observation，而非单帧图像。

#### O1. 斜板滚球接取（Ramp Ball Catching）

小球沿斜板滚动，机器人观察其早期运动后，将接收盘放到预测落点。随机变量包括斜率、摩擦系数、球的质量与半径、初速度和表面材质。

#### O2. 弹跳球落点拦截（Bounce-and-Intercept）

机器人观察球的首次下落或弹跳，推断恢复系数与速度，在后续弹跳发生前选择拦截位置和时机。

#### O3. 传送带分拣（Motion-Aware Conveyor Sorting）

多个物体以不同且可能变化的速度经过传送带。机器人由运动历史估计速度和加速度，选择抓取顺序、抓取点及启动时刻。

#### O4. 滑落前支撑（Preemptive Slip Support）

物体在斜面或托盘上逐渐滑动。机器人根据微小位移和加速趋势判断哪个物体最先掉落，并提前放置支撑或完成抓取。

#### O5. 倾倒流量预测（Pouring Flow Anticipation）

机器人观察颗粒或液体的初始流动，估计流速和剩余倾倒时间，选择合适容器并调整其位置，避免溢出或漏接。

该类任务应满足：

- 决策前存在明确观察阶段；
- 单帧观测不足以确定最优动作；
- 不同物理参数会产生可观测的运动差异；
- 观察结束后的行动具有有限时间窗口。

### 4.2 Probe for Decision

关键属性无法仅由初始视觉可靠识别。机器人必须选择 informative action，并主要通过 **夹爪开合状态、关节位置以及物体的可见位姿/形变/运动响应** 降低不确定性，再完成任务。力觉、触觉与音频可以作为未来扩展，但不能成为基于 DOMINO 的核心评测前提。

#### P1. 异常尺寸小球质检（Size Anomaly Inspection）

多个外观相近的小球中存在尺寸异常项。机器人通过抓取闭合量、接触状态或夹爪反馈识别异常球，并将其放入异常盒。

#### P2. 隐藏重量分拣（Weight-Aware Sorting）

外观相同的物体质量不同。机器人通过施加统一的提起或轻推动作，主要根据物体是否被成功抬起、位移/加速度响应、夹爪状态及视觉运动差异推断重量，再将其放到匹配的容器中。若缺少稳定力觉接口，不将关节力矩作为必要输入。

#### P3. 软硬度检测与抓取（Stiffness-Aware Grasping）

机器人通过按压或轻夹估计刚度，然后选择抓取力度。力度过大可能损坏软物体，过小则可能导致滑落。

#### P4. 摩擦探测与运输（Friction-Aware Transport）

机器人先执行短距离试推，依据力和位移响应判断摩擦，再决定推、抓、抬升或选择更安全的路径。

#### P5. 容器内部状态识别（Container Content Inspection）

外观相同的封闭容器可能为空、含固体或含液体。机器人通过提起、倾斜或晃动，从容器和内部可见部件的动态响应判断状态，再决定搬运策略。该任务只有在 DOMINO 中能通过视觉或 qpos 稳定表达差异时才纳入核心集；音频和力矩版本属于扩展协议。

该类任务应满足：

- 隐藏属性不能被纹理或外观 shortcut 稳定预测；
- 提供信息增益和代价不同的 probing actions；
- 探测具有时间、能量或风险成本；
- 专家应以较少、较安全的探测解除关键不确定性。

### 4.3 Simulate for Decision

这一类不再泛指“从若干连续动作中挑一个效果最好的”，否则容易与 Observe 和 Probe 重叠。它专门考察 **structural causal foresight**：关键证据已经存在于当前场景的几何、接触、支撑、遮挡、铰接和约束关系中，但危险后果尚未发生。机器人必须在行动前推演：

> **If I change this relation, what chain of physical events will follow?**

它与前两类的边界是：

- **Observe**：需要看一段自然运动，才能估计运动状态或动力学；
- **Probe**：需要先做信息获取动作，才能揭示隐藏属性；
- **Simulate**：不要求等待或试探；原则上当前结构已经提供充分证据，但需要物理因果推演才能选对动作。

#### S1. 倚门杯取出（Leaning-Cup Door Choice）

一个杯子倚靠在双门柜的右门内侧。直接打开右门会移除支撑，使杯子跌落；为了安全取杯，机器人必须打开左门，或先从左侧扶住杯子再操作右门。成对场景可将杯子改为倚靠左门，使正确选择反转。

#### S2. 门体扫掠避碰（Door-Sweep Avoidance）

目标物和易碎物位于门或抽屉的未来扫掠空间内。机器人必须预判 articulation 的扫掠体积，选择另一扇门、先移走障碍，或采用分阶段开门，不能等碰撞发生后再纠正。

#### S3. 支撑链取物顺序（Support-Chain Retrieval）

多个物体形成支撑关系，目标物位于结构中。抽走某个承重物会导致上方物体倒塌；机器人需要推演支撑图的变化，选择安全的拿取顺序或先添加临时支撑。

#### S4. 受阻抽屉开启（Blocked-Drawer Planning）

抽屉内的高物体、倾斜物或外部障碍会在抽屉打开时与柜体发生碰撞、卡住或倾倒。机器人需从当前布局推演抽屉运动产生的后果，选择半开后清障、先移物或改用另一开口。

#### S5. 约束释放与回弹（Constraint-Release Planning）

物体被绳带、挡板或压紧结构约束。直接解除某一约束会使储存的势能释放，导致物体弹出或另一部件下落；机器人需选择正确的释放顺序、先固定受影响物体，或从安全方向操作。

该类任务应满足：

- 关键因素是当前可感知的结构关系，而不是不可见的材质标签；
- 至少两个动作在局部看来可执行，但会触发不同事件链；
- 错误动作造成跌落、碰撞、卡死或损坏等不可逆后果；
- counterfactual intervention 只改变一个支撑、接触或约束关系，并使正确决策反转；
- 同时评价结构关系理解、事件链预测和最终动作选择。

---

## 5. 训练数据规划

### 5.1 统一 Episode 数据结构

每条数据建议包含：

1. **Task specification**：语言指令、目标条件和安全约束。
2. **Core policy observations**：DOMINO 可稳定导出的多视角 RGB 与机器人 qpos；depth、segmentation 或其他状态只有在完整采集链验证后才加入。
3. **Actions**：14D absolute joint target、时间戳、控制频率和执行阶段标签。
4. **Privileged physical state**：质量、摩擦、惯性、恢复系数、刚度、阻尼、速度、加速度和接触状态等。
5. **Outcome annotation**：成功、失败类型、碰撞、损伤、完成时间、安全代价，以及可由 action/qpos 计算的控制代价 proxy。
6. **Phase annotation**：observe、probe、simulate/commit、execute 等阶段边界。
7. **Counterfactual identity**：共享几何/外观配置、仅改变物理参数或动作的 episode group ID。

Privileged state 用于辅助监督、构造 oracle、诊断失败及设计数据切分；标准测试时不应默认直接提供给 policy。

### 5.1.1 DOMINO Observation Contract 与特殊限制

ForesightBench 当前基于 DOMINO/RoboTwin/SAPIEN codebase 开发。现有数据链已明确验证的核心字段是：

- head / left-wrist / right-wrist RGB；
- 14D robot qpos；
- 14D absolute joint target actions；
- episode、scene metadata 和任务脚本可访问的 simulator state。

当前不能默认获得跨 embodiment 一致、可直接用于 policy 的：

- 六维末端力/力矩；
- 关节 effort / torque；
- 触觉阵列；
- 音频；
- 稳定且统一的 qvel、末端位姿或接触冲量字段。

因此必须区分三层数据：

1. **Core observation contract**：RGB history + qpos + instruction。所有 baseline 和主榜单只能依赖这一层。
2. **Privileged simulator annotations**：质量、摩擦、速度、加速度、接触关系、articulation qpos 等，由 task/simulator 离线导出，用于监督、oracle 与诊断，但默认不在测试时提供。
3. **Optional sensor extensions**：力觉、触觉、音频或额外 proprioception。只有完成采集、转换、训练与 sim-to-real 一致性验证后，才作为独立扩展赛道，不能与核心结果混报。

这意味着 Probe 任务不能把“读取精确力矩数值”设为必要条件。任务必须能从 DOMINO 已有通道中产生可辨别证据，例如夹爪闭合量、能否抬起、物体位移、视觉形变、滑动距离、摆动轨迹或 articulation 状态变化。若某个隐藏属性只能通过当前不存在的力/触觉传感器识别，则应降为扩展任务，而不是进入 v1 核心 benchmark。

### 5.2 Observe for Decision 数据

除专家轨迹外，保存：

- 质量、尺寸、惯性张量和质心；
- 静摩擦/动摩擦系数、恢复系数、阻尼和斜面参数；
- 每一时刻的位置、姿态、线速度、角速度和加速度；
- 接触点、接触力及碰撞事件（仅作为 simulator privileged annotation，不作为 policy 输入）；
- 离开斜板、首次弹跳、预计落地等关键事件时间；
- 真实未来轨迹和目标事件 ground truth。

专家轨迹包含：

1. **Observation phase**：机器人观察或调整视角，物体自然运动，保留充分 temporal context。
2. **Execution phase**：机器人依据观察启动接取、支撑、抓取或容器放置。

额外生成 10%、30%、50% 和 100% 等 observation-length variants，分析证据量与决策准确率的关系。

辅助训练目标可以包括物理参数估计、速度/加速度估计、关键事件时间预测、未来轨迹预测和最终动作预测。

### 5.3 Probe for Decision 数据

除最终专家轨迹外，保存：

- 真实质量、尺寸、刚度、摩擦和内部内容等隐藏属性；
- 核心输入中的夹爪开合量、机器人 qpos 和多视角 RGB history；
- 提升高度、推动距离、运动速度和晃动频率等探测参数；
- 探测前后的位姿、形变和运动响应；
- 每次 probing 后的 belief 或属性后验；
- 探测时间、能量、风险和不可逆改变等成本。

六维末端力/力矩、关节 effort、触觉阵列和音频只在传感链完整验证后作为 optional extension 保存，不属于 v1 必需字段。

专家轨迹包含：

1. **Initial uncertainty**：初始视觉无法唯一确定属性。
2. **Probe selection**：专家选择高信息增益动作。
3. **Interaction response**：至少记录 RGB、qpos、夹爪状态以及不同属性物体的可见运动响应。
4. **Decision and execution**：依据探测结果完成最终操作。

除最优探测外，采样低信息、冗余或高风险探测，以学习“什么动作值得尝试”，而不只是模仿固定 probing sequence。

辅助目标包括属性分类/回归、information gain 预测、belief update、下一最佳探测动作和最终决策。

### 5.4 Simulate for Decision 数据

这是区别于普通 imitation dataset 的关键。对同一初始结构状态 $s_0$，执行或仿真多个离散、语义清晰的候选 intervention：

$$
\mathcal{D}(s_0)=\{(a_i,\tau_i,e_i,r_i,c_i,y_i)\}_{i=1}^{K},
$$

其中 $a_i$ 是候选动作（如开左门/开右门/先支撑），$\tau_i$ 是未来状态轨迹，$e_i$ 是结构化事件链，$r_i$ 是任务收益，$c_i$ 是跌落、碰撞、损坏等代价，$y_i$ 是成功或失败标签。

每个任务额外保存：

- 初始接触、支撑、containment、articulation 和约束关系图（作为离线监督与诊断标签，不直接提供给核心 policy）；
- 候选高层 intervention 及对应的统一低层执行轨迹；
- 每个动作对应的未来 RGB、物体状态和机器人状态；depth 仅在采集链验证后作为附加数据；
- 事件标签与时间，如 support-removed、door-sweep-contact、object-falls、drawer-jams；
- 成功率、碰撞、物体倾角/跌落、不可达状态、damage proxy 和安全违规；
- 失败原因，如支撑移除、扫掠碰撞、结构倒塌、卡死或约束突然释放；
- oracle action ranking 和候选动作间的偏好；
- paired counterfactual 中被改变的唯一结构关系。

候选动作建议混合：

- oracle 安全动作；
- 局部看似合理、但会触发延迟危险的 hard negative；
- “先支撑/先清障”等多阶段安全动作；
- matched control 中安全、但在 intervention 场景中失败的同名动作。

数据支持 relation recognition、event-chain prediction、action-conditioned future prediction、成功/失败预测、pairwise preference learning 和 counterfactual action selection。失败 rollout 仍然重要，但它服务于学习结构性因果后果，而不是把第三类退化为一般性的连续控制调参。

### 5.5 数据规模与切分

- 3 个能力类别，每类 5 个 task families，共 15 类任务；
- 每类任务生成大量物理参数和外观组合；
- 每个 Observe episode 提供多个观察长度版本；
- 每个 Probe 初始状态提供多个探测动作及传感响应；
- 每个 Simulate 初始结构提供 $K$ 个候选 intervention、事件链及其未来后果；
- 仿真数据为主，选 4–6 个代表任务进行真实机器人验证。

测试集包含：

- **Visual OOD**：新纹理、背景和物体外观；
- **Physical OOD**：训练范围外的质量、摩擦、弹性、刚度或速度；
- **Compositional OOD**：见过单个属性范围，但未见过其组合；
- **Action OOD**：新的动作参数或动作组合；
- **Sim-to-Real**：仿真训练后在真实物理系统中测试。

---

## 6. Benchmark 设计原则

### 6.1 Physically Aliased Scenarios

构建成对或成组场景：视觉几何和语义任务几乎相同，但隐藏物理状态不同，最优决策也不同。

### 6.2 Evidence-Controlled Evaluation

对同一任务控制模型获得的证据：

- 单帧观测与完整运动历史；
- 允许或禁止 probing；
- 提供或不提供 oracle physical state；
- 提供或不提供 action-conditioned future。

这种 controlled ablation 可以定位增益究竟来自视觉识别、动态观察、主动交互还是后果预测。

### 6.3 Irreversibility and Commitment

任务应包含有限时间窗口、不可逆事件或明确错误代价，使模型必须在证据充分与及时行动之间权衡。

### 6.4 Task-Relevant Prediction

Benchmark 不把视觉逼真的未来视频作为终点，而衡量预测是否改善最终决策：

> **Visual plausibility is not physical understanding; a useful forecast must support better action selection.**

### 6.5 Visual Appeal and Communicability

任务不仅要科学有效，也应具有良好的视觉表达和传播效果。优先选择因果关系清楚、动作后果显著、无需长篇解释即可理解的视频场景，例如小球落入接盘、杯子因错误开门跌落、支撑移除后结构倒塌。

具体要求：

- clean 与 failure outcome 在短视频或 GIF 中一眼可辨；
- 使用构图清楚、色彩统一且具有适当材质质感的场景资产；
- 关键物体、候选动作和危险区域在主相机中清晰可见；
- 单个 demonstration 最好在数秒到十余秒内讲清问题；
- 场景设计适合论文 figure、项目主页、talk 和社交媒体传播；
- 视觉美观不能依赖会改变物理规律的后处理，也不能让纹理泄漏答案。

可以将 **visual legibility** 作为任务进入主 benchmark 的工程门槛：如果人类观看者无法快速理解“机器人为什么选错”，该任务更适合作为诊断扩展，而不是宣传主任务。

### 6.6 Low-Friction Evaluation

Benchmark 的影响力很大程度取决于第三方能否低成本跑通。代码发布应优先做到：

- 一条命令完成环境安装，或提供经过验证的 container；
- 一条命令运行 smoke test，一条命令运行标准评测；
- 支持少量 episode 的本地调试模式和完整 benchmark 模式；
- 自动下载或校验资产、模型接口和配置版本；
- 固定 seed、任务版本、物理步长、相机和 evaluator contract；
- 自动输出逐任务指标、汇总表、失败原因和可视化视频；
- evaluator 完全程序化，不依赖人工观看打分；
- 失败时提供清楚的日志，而不是静默返回零分；
- 发布最小可运行示例，避免用户先理解整个 DOMINO 内部实现。

建议设置分层评测：

1. **Smoke suite**：每类 1 个任务、少量 seed，验证安装和接口；
2. **Core suite**：论文主表使用的标准任务与固定 episode 数；
3. **Full/OOD suite**：完整物理泛化、反事实和 sim-to-real 评测。

### 6.7 Compatibility with Existing Robot Codebases

ForesightBench 应尽量复用现有生态的 observation/action/data contract，使 StarVLA、RoboTwin、DOMINO 以及其他 VLA policy 可以低改动接入。

优先兼容：

- RoboTwin/DOMINO 的 task class、配置、资产和数据采集入口；
- 标准多视角 RGB、qpos 和 14D absolute joint action；
- ALOHA-style HDF5 与 LeRobot 格式转换；
- StarVLA 现有训练、推理和 rollout wrapper；
- 常见 policy 的统一 reset / observe / act / step adapter。

工程上应避免要求每个 baseline 修改模型主体。推荐接口结构：

    Policy Adapter
      model-specific observation preprocessing
      model-specific action decoding
                ↓
    Canonical ForesightBench Interface
      RGB history + qpos + instruction
      14D absolute joint target
                ↓
    DOMINO / RoboTwin Environment + Evaluator

每个新模型原则上只需要实现一个薄 adapter，即可运行全部任务。若模型使用不同 action representation，应在 adapter 中转换，并严格共享相同的低层控制器、速度/加速度限制和 decision frequency，避免接口差异污染算法比较。

### 6.8 Reproducibility and Versioned Contracts

Benchmark 必须把容易造成结果漂移的因素显式版本化：

- simulator、DOMINO/RoboTwin commit 和资产哈希；
- task config、随机种子和数据 split；
- observation history、action frequency、action chunk 与控制上限；
- success/failure predicate 和评分脚本；
- policy adapter 版本及任何 action post-processing。

每次评测应生成 machine-readable manifest，使结果能够复查和精确复现。排行榜应拒绝观测、动作或 oracle 信息不符合标准 contract 的结果，或将其列入独立赛道。

### 6.9 Diagnostic Value over Task Count

优先构建少量但具有明确失效解释的 task family，而不是堆叠大量相似任务。每个任务都应回答一个具体问题：

- 模型是否从运动历史中提取了必要证据？
- 模型是否选择了有效的 probe？
- 模型是否理解了支撑或接触关系？
- 模型是否预测了错误动作的事件链？
- 失败来自物理理解、动作选择还是低层执行？

每个任务应配套 oracle-state、oracle-decision 和 oracle-execution 等分层上界，以及 matched control 和 counterfactual intervention。这样主结果不仅是 success rate，还能形成有说服力的能力诊断。

### 6.10 Scalable Generation and Stable Physics

任务必须能在可接受的 rejection rate 下批量生成，并在固定 seed 上稳定复现。进入 core suite 前应通过：

- 大批量 reset、rollout 和渲染稳定性测试；
- paired counterfactual 的唯一最优动作验证；
- evaluator 对小幅数值噪声的鲁棒性检查；
- 资产许可、体积和下载可靠性检查；
- success、near-failure 与 failure bucket 的分布审计。

对于 SAPIEN 中不稳定或不存在的机制，例如真实碎裂、复杂液体和高保真软体，应采用公开透明的 damage/risk proxy，或降为扩展任务。不要让核心结论依赖难以复现的偶然物理接触。

### 6.11 Accessibility and Hardware Independence

核心 benchmark 不应绑定昂贵传感器、专有硬件或单一 GPU 配置。主赛道依赖 DOMINO 已验证的 RGB、qpos 和标准动作接口；力觉、触觉、音频和真实机器人结果作为独立扩展。

同时建议提供：

- 可直接下载的离线 observation-action-outcome 数据；
- 无需启动仿真器的 perception/reasoning 子任务；
- 不同计算预算下的推荐 episode 数；
- 可并行运行和断点续评的评测脚本。

这样既能让机器人实验室完成闭环评测，也能让 CV/world-model 社区先在离线预测和决策任务上参与。

### 6.12 Task Admission Priority

新增任务不应只按“想法是否有趣”决定是否投入开发。建议按以下顺序筛选：

1. **Scientific necessity**：正确决策是否真的依赖物理证据或事件推演？
2. **Causal controllability**：是否能通过单变量 intervention 稳定改变最优动作？
3. **DOMINO feasibility**：现有 observation、action、资产和物理机制是否足以实现？
4. **Evaluation stability**：能否自动评分、固定 seed 复现并区分失败原因？
5. **Ecosystem compatibility**：是否可直接使用 StarVLA/RoboTwin/DOMINO 接口？
6. **Visual communicability**：结果是否适合用短视频和 figure 清楚展示？
7. **Generation scalability**：能否低成本生成足够多的训练与测试变体？

其中前四项是进入 core suite 的硬门槛；后三项决定开发优先级和是否适合作为 benchmark 的主宣传任务。可以为候选任务建立 1–5 分的 rubric，优先开发总分高且不存在硬门槛缺陷的任务。

从当前候选看，**斜板滚球接取、异常尺寸质检和倚门杯取出**分别代表 Observe、Probe 和 Simulate，概念互补、视频可读性强，也较适合作为第一批 flagship tasks。

---

## 7. 评价指标

- **Task Success**：最终任务成功率。
- **Physical State Estimation Error**：质量、摩擦、速度、刚度等属性的估计误差。
- **Probe Efficiency**：单位探测成本带来的不确定性降低或成功率提升。
- **Outcome Prediction Error**：候选动作未来状态或结果的预测误差。
- **Action Ranking Accuracy**：候选动作优劣排序准确率。
- **Event-Chain Accuracy**：支撑移除、碰撞、跌落、卡死等关键事件及顺序的预测准确率。
- **Decision Regret**：模型动作与 oracle 最优动作之间的收益差。
- **Counterfactual Consistency**：物理参数改变后，模型是否相应改变预测和决策。
- **Anticipation Margin**：不可逆事件发生前多早完成关键动作。
- **Uncertainty Calibration**：置信度是否匹配真实误差或成功概率。
- **Adaptation Gain**：获得观察或交互证据后，相比静态观测基线的提升。

综合指标可写为：

$$
\text{Foresight Score}
= \text{Task Utility}
- \lambda_1\text{Decision Regret}
- \lambda_2\text{Probe Cost}
- \lambda_3\text{Risk Cost}.
$$

主论文仍应报告分项结果，避免综合分数掩盖模型在 Observe、Probe 和 Simulate 环节的不同短板。

---

## 8. 核心实验与论文结论

论文可以验证：

1. 当前 VLA 在静态视觉足以决定动作的任务上表现较好，但在 physically aliased scenarios 中显著下降。
2. 完整运动历史相比单帧输入显著改善 Observe 类任务。
3. 提供 oracle physical properties 后性能显著提升，说明隐藏物理状态推断是关键瓶颈。
4. 即使允许主动交互，部分模型也不会选择高信息增益的 probing action。
5. 只使用成功轨迹训练的模型难以学习“移除支撑 → 物体失稳 → 跌落”等事件链；加入错误动作 rollout 和反事实结构变体后，事件预测与决策能力提升。
6. Simulate 类任务中的 paired intervention 只改变支撑/接触关系，却会使正确动作反转，可检验模型是否真正理解结构因果而非记忆“总是开左门”等 shortcut。
7. 视频预测的感知质量与任务成功率可能弱相关，task-relevant event prediction 更重要。
8. 更大的 VLM 或更高控制频率，不一定自然带来更好的 decision-relevant physical intelligence。

核心结论：

> **Reliable embodied decision-making requires more than recognizing the current scene. It requires acquiring physical evidence, understanding interaction feedback, and anticipating the consequences of alternative actions.**

---

## 9. 标题与命名建议

推荐标题：

> **ForesightBench: Evaluating Decision-Relevant Physical Intelligence in Embodied Agents**

其他候选：

- **ForesightBench: Observe, Probe, and Simulate for Embodied Decision-Making**
- **ForesightBench: Can Robots Acquire the Physical Knowledge Needed to Decide?**
- **PhysDec: A Benchmark for Decision-Relevant Physical Intelligence**
- **OPS-Bench: Observe, Probe, and Simulate for Physical Decision-Making**

摘要中的一句话定义：

> **ForesightBench evaluates whether embodied agents can extract physical evidence from temporal observation, reveal latent properties through active interaction, simulate action-triggered causal events from physical structure, and use this knowledge to make effective decisions.**

---

## 10. 核心贡献表述草案

1. 提出 **decision-relevant physical intelligence**，将物理理解定义为服务于具身决策的证据获取与后果预测能力。
2. 建立由 **Observe for Decision、Probe for Decision、Simulate for Decision** 组成的统一评估框架。
3. 通过 physically aliased scenes、隐藏物理属性和同状态多动作分支，抑制静态视觉与任务模板 shortcut。
4. 发布同时包含专家轨迹、privileged physical annotations、多模态交互状态以及成功/失败反事实后果的数据集。
5. 系统分析 VLA、VLM、world model 和传统规划方法在观察、试探、预测与决策各环节的能力缺口。

最终应让读者记住的不是“ForesightBench 有 15 个新任务”，而是：

> **A robot should not only know how to act; it should know what physical evidence to acquire and what its actions are likely to cause before deciding how to act.**
