# FG26 的 LLM 语料

## 直接使用哪些文件

- `train.jsonl` 和 `val.jsonl` 是最终对话文件，仅在全量回读通过后发布。共 1,427,082 条，其中 train 为 1,355,530 条、val 为 71,552 条。
- `preview.jsonl` 是从正式语料逐条原样选出的 140 条预览，覆盖两个 split 的所有启用任务与输入模式，不是另一份训练集。
- `corpus_report.json` 提供实际任务数、模板使用频次、光谱组合分布、文件哈希和验收状态。完成标记为 `accepted_full_conversation_readback`。
- `FG26_query_response_templates_expand.json` 是唯一的正式模板与数量配置。
- `structures/{key_id前两位}/{key_id}.xyz` 是 233,948 个已导出的结构；每条结构输入语料均有直接可读的 `input_xyz_path`。
- 光谱没有重复导出。每条光谱语料的 `input_spectrum_refs` 直接定位原始官方 parquet，`spectrum_index.jsonl` 提供全量有效通道及不可用原因，`spectrum_audit_report.json` 提供检查统计。
- `structure_index.jsonl`、`xyz_export_report.json` 保留原始结构、性质和计算方法溯源。原始数据未修改或删除。

模型只接收选中的结构或光谱数值、必要模态信息和 `messages[0].content`，以 `messages[1].content` 为回答目标。**不要把整条 JSON 当作 user prompt**。记录 ID、路径、哈希、标签、模板 ID 和计算方法均是加载或溯源元数据，不应作为模型输入。

## 任务与数量

| 输出任务 | 3D 结构输入 | 光谱输入 |
| --- | ---: | ---: |
| SELFIES | 233,948 | 467,896 |
| HOMO 能量 | 58,487 | 0 |
| LUMO 能量 | 58,487 | 0 |
| 偶极矩模长 | 58,487 | 0 |
| 各向同性极化率 | 58,487 | 0 |
| 分子式 | 116,974 | 116,974 |
| 阳性官能团或结构片段 | 116,974 | 116,974 |
| 是否含芳香环系统 | 5,849 | 5,848 |
| 事实组合描述 | 5,848 | 5,849 |
| 合计 | 713,541 | 713,541 |

分子式和官能团各选 116,974 个不重复的 authority 记录；同一任务的两个输入模式使用同一批记录。官能团只从至少一个阳性标签的记录中选。四项标量任务将全部记录分成四组，每条记录分配一个标量任务，不是每条生成四个标量问答。SELFIES 对每条记录生成一条结构输入和两条不同谱组合输入。

一条对话只含一种输入模式，不要求同时给结构和谱。光谱描述仅包含分子式、芳香性、阳性结构片段；不夹带数值性质。SCF 总能量和 HOMO–LUMO gap 不作为问答或描述目标，原始索引中保留这些值。

## 记录范围与划分

仅使用 authority 的 233,948 个 `record_index`，来自

`/mnt/e/Datasets/fg26/04_training_data/repository_data/phase15_aux/canonical_selfies_by_record_index_v17_nonisomeric.jsonl`

唯一划分依据为

`/mnt/e/Datasets/fg26/04_training_data/repository_data/split_maps/phase2_v26_record_split_map.jsonl`

原始记录为 222,218 train 和 11,730 val。同一记录的所有任务、模态和谱组合保持原 split。各任务数量在原 split 内按比例分配并做最大余数取整。最终对话条数比原始分子记录数大，不是重新划分了分子。

不用 metadata CSV 的旧 split，也不用官方谱文件名中的 train/test 决定本轮 split。CSV 旧 split 与本轮有 22,319 条不同。额外 `record_index=39469` 不在 authority 中，未纳入，也未删除原记录。

233,948 是记录数；去立体 canonical SMILES 有 226,537 个不同字符串，跨 train/val 的这些字符串交集为零。这不等同于所有构象、互变异构或外部基准泄漏都已审计。

## 模板多样性

本轮主 agent 与 subagent 重新扩展并独立交叉检查。

| 任务 | 核心 query | response |
| --- | ---: | ---: |
| 分子式 | 16 | 6 |
| HOMO 能量 | 16 | 6 |
| LUMO 能量 | 16 | 6 |
| 偶极矩模长 | 16 | 6 |
| 各向同性极化率 | 16 | 6 |
| 阳性官能团或结构片段 | 16 | 8 |
| 芳香环系统存在性 | 16 | 16，肯定和否定各 8 |
| SELFIES | 16 | 1，纯原字符串 |
| 事实组合描述 | 16 | 6 |

共 144 条核心 query、61 条 response，另有结构、单谱、多谱各 20 条前提句，共 60 条。前提不再集中使用被动的 provided，包含 We give you、We supply、We are sharing、Let's work with、Use、Examine、Consider、Start from 等句式。每组只有 1/20 的前提使用 provided。

完整 user 由一条符合实际输入的前提加一条核心问题组成，例如

- We give you the three-dimensional structure of a molecule. What is the molecular formula of this molecule?
- Let's work with the infrared spectrum of this molecule. Represent this molecule in SELFIES.
- Examine the infrared, Raman, and UV spectra of this molecule before answering. Identify some functional groups or structural motifs present in this molecule.

描述有 9 种不重复的性质组合、32 条事实句。其中 3 种组合允许谱输入，全部仅含图结构标签；无 FG 阳性记录可用分子式加芳香性组合。其余包含数值的组合仅用于 3D 输入。描述不自动附加 SELFIES，也不写稳定性、合成方法或无证据原因解释。

问法、前提、回答用独立随机打乱的模板序列抽取，在同 split、任务、输入模式和适用子组内均衡使用。芳香性先选正确正负池，描述先选允许的组合再选事实句。各兼容池内模板使用次数相差不超过 1，不强行改变芳香性标签分布，也不为模板穷举复制语料。

user/assistant 只有两条消息，没有 system、冒号、CIF/XYZ 文件称呼、输入内容占位符或未填槽位。SELFIES 是明确的输出目标，不是输入几何占位符；其回答保持完整原字符串，不加引导语或标点。

## 光谱组合与加载

八类候选通道为 IR、Raman、UV、broadened hydrogen NMR、broadened carbon NMR、carbon XAS、nitrogen XAS 和 oxygen XAS。

按每个原 split、每个启用光谱任务分配谱种数量。1 至 8 种分别为 25%、25%、20%、15%、8%、4%、2%、1%，一至四种占 85%。这是起步采样方案，不是训练消融证明的最佳比例。小数取整使用最大余数法，随机种子为 20260913。

仅在当前记录真正有效的通道中随机选择，保证配额可满足。同一记录、同一任务不重复相同组合；两条谱到 SELFIES 可以是任意两种不同组合，不固定“完整谱”或“缺谱”角色。前提中提到的谱名、`spectrum_types`、引用顺序和实际加载数据必须一一对应。

逐条绑定和数值检查结果

| 通道 | 非空、有限且非全零 | 空数组或全零，不参与采样 |
| --- | ---: | ---: |
| IR | 233,948 | 0 |
| Raman | 233,948 | 0 |
| UV | 233,947 | 1 |
| broadened hydrogen NMR | 229,308 | 4,640 |
| broadened carbon NMR | 233,033 | 915 |
| carbon XAS | 233,070 | 878 |
| nitrogen XAS | 194,065 | 39,883 |
| oxygen XAS | 201,418 | 32,530 |

所有 authority 记录均至少有四种有效谱，分布为 4 种 82 条、5 种 504 条、6 种 8,817 条、7 种 59,373 条、8 种 165,172 条。空数组与全零的具体原因分开记录，未把整条分子删除，也没有补零后冒称有谱。全零只说明该数组不适合作为本轮有信号输入，不据此判定整个分子标签错误。

官方每种谱共 238,869 行，其中 4,921 行不属于 authority。逐种独立以 `SHA256(key)=key_id` 关联，不能依赖不同文件的行位置相同。原 `key` 是分子 SMILES，仅用于绑定核对，绝不送入模型。

每个引用包含 `source_path`、`row_group`、`row_in_group`、`row_index`、`dtype`、`shape`、`key_id`、`data_sha256` 和 `axis_metadata_id`。通过 pyarrow 读对应组，取组内行，从二进制 `data` 按 `dtype` 解码并按 `shape` 恢复即可；所有位置均为零基。重新加载时检查 key 的 SHA256 和数据字节 SHA256。

正式保留原始 float64 的 4,000 点数组，不归一化、不插值、不补零、不重新推导峰。单个 test parquet 是大 row group，训练时应按文件或组批量读取、缓存，不要为每个对话重新读整个文件。

**横轴与单位边界**：官方 parquet 仅有 key/dtype/shape/data，没有物理轴或强度单位元数据，官方 HF 页面目前也无 dataset card。模板共享元数据使用原始 `sample_index=0..3999`，未知 `physical_axis` 和 `intensity_unit` 保留 null，不猜测 NMR/XAS 的 ppm/eV 范围。本地此前 IR/Raman 与 Gaussian 频率的抽样核对支持 1..4000 cm^-1，作为单独的本地证据保留，不冒称全部通道已有官方横轴定义。因此本轮没有峰位读取、谱轴换算或定量强度问答。

## 结构、标签和证据边界

XYZ 已从原始 extxyz 导出，保留坐标数字、显式氢和原子顺序，单位 Å，第二行为空，没有原注释的能量、偶极矩或标识信息。不从 SMILES 重新生成，不添加晶胞或周期性边界。

此前全量结构导出检查已完成原始结构、性质、NPZ 与 metadata 绑定。原始坐标转 float32 后全部复现 NPZ；XYZ 写出回读一致。六项原标量存在、有限，并与原始 properties.json 在缓存对应精度下一致。本轮用源文件哈希固定这些证据，不把模板扩展误称为新增全库三维键级恢复。

数值统一取 B3LYP、AUG-CC-PVDZ、OPT+FREQ、RB3LYP 的本地解析字段。HOMO/LUMO 输出 4 位小数 eV，偶极矩 4 位小数 D，各向同性极化率 2 位小数 a.u.；显示位数不表示科学精度。5,780 条记录有负振动频率，所以不将所有结构描述为稳定极小值。没有重新运行量化计算或重解析原始 Gaussian 日志。

官能团沿用原 47 个 SMARTS、同位点优先级和启用的 26 类，不重打标签、不换成另一套分类。原规则文件为 `/home/lmy/SpectraAtom-LLM/scripts/fg_author_47_policy.py`。回答只陈述已检出的阳性官能团或结构片段，不保证穷尽，不由二值标签推断数量，也不由被抑制的零标签生成一般否定。含义较宽的 SMARTS 使用准确片段措辞，例如 sulfide 的 [SX2] 不收窄为必有 C–S–C 的硫醚。892 条无当前阳性 FG 记录仅不参加对应问答，不说“没有官能团”。

芳香性固定用修正后的 `aromatic`，即分子图中至少一个 RDKit 芳香原子。233,948 条中阳性 27,562、阴性 206,386；不用旧苯环规则 `aromatic_phase2_label`。融合边界 41529、47358、51164 说明应写 aromatic ring system，不保证 RDKit 将某个单独环计为芳香环。两套旧新字段差异 16,846 条，不是本轮重新发现这么多错误标签。

SELFIES 固定为 authority 的 nonisomeric 版本。本轮全 233,948 条再次成功解码并匹配 authority 的去立体分子图。16 个问法中 12 个普通、4 个明确省略立体信息；所有问法沿用同一输出策略，不声称恢复手性或 E/Z。

此前 20 条结构到图抽查中，连接关系全部匹配，19 条可恢复相同或表示等价的键级图；138629 的自动键级恢复仍未解决，不能据此判定原标签错误。本轮没有新增全库 XYZ 键级审核。谱到 SELFIES 是有来源绑定的监督配对，不意味着任何单谱都可唯一反推出分子。

## 验收与复现

`build_llm_corpus.py` 分阶段执行，遇到不可满足配额或错误绑定会报错，拒绝覆盖已有正式语料。日志在本轮临时工作目录，正式结果和报告集中在本目录。

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 /home/lmy/miniconda3/bin/python3 build_llm_corpus.py templates
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 /home/lmy/miniconda3/bin/python3 build_llm_corpus.py verify
```

首次构建顺序是 audit、generate、verify。已有 spectrum_index 和正式语料时不要重复运行 audit/generate；verify 可以重新回读现有语料。未通过验收的暂存文件以 .partial 结尾，不用于训练。

验收逐条检查角色、禁止文本、已填答案、模板 ID、原始 split、数值与单位、芳香性分支、FG 阳性标签、描述模块与输入模式、完整 SELFIES、谱名与实际引用、重复记录和谱组合。preview 与正式文件中的同 ID 完整对象精确比较，而非独立重新生成。结构文件全量清点，另抽 64 个回读内容与哈希；16 个光谱源文件各抽 4 条重新读数组、核对 key/数据哈希和定位偏移。

自动模板检查覆盖 411,117 项；subagent 另用 8 条真实记录完成 26,112 条渲染组合和 11 类负例测试。该子测试的谱引用明确为 mock，不冒充实际谱检查；真正的全量原始谱验收独立记录在 spectrum_audit_report.json。
