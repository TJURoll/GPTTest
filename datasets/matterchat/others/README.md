# MatterChat LLM corpus

- 训练使用 `train.jsonl`；验证使用 `val.jsonl`；`gnome.jsonl` 是独立外部评估，不并入训练。
- 12 种任务、91 条问题模板：83 条作者核心问句、1 条作者 General 问句、7 条确认的描述扩展。
- 每条记录仅有 user/assistant 两条消息。结构通过 `structure_id` 关联 `structures.jsonl`，不在消息中放结构正文、CIF、占位符或 system prompt。
- `train.jsonl` 和 `val.jsonl` 的每条记录另有顶层 `cif_path`，例如 `cif/train/mp-1034825.cif`，相对于本目录；读取时使用 JSONL 文件所在目录拼接该路径。路径不进入 `messages`，原 `geometry_sha256` 保留。
- `preview.jsonl` 中对应 train/val 的 96 条样本已同步路径；GNoME 部分及 `gnome.jsonl` 本次未改，仍可通过 `structure_id` 和 CIF 索引定位。
- `structures.jsonl` 仅导出晶格（Å）、元素/占位和分数坐标，去掉 magmom、计算标签等目标相关附加字段。训练时只取几何字段，不把 ID、来源、split 或 metadata 当模型输入。
- 每个适用材料—任务一条，任务/子组内模板均衡随机分配。文件按任务组织，训练数据加载器应打乱样本顺序。
- `preview.jsonl` 是最终三个划分的逐字抽取子集，不能当作另一个训练划分再重复加入。
- `skipped_tasks.jsonl` 记录未通过条件的材料—任务及原因；不自动删除原始记录，也不宣称这些结构一定错误。
- `report.json` 给出计数、来源/输出哈希、校验参数和未通过项。实验观察任务已停用。
- GNoME 缺少的约简式和晶系由结构推导，来源写入 metadata；不使用 `_processed` 性质字段或 `structure_mace` 替换原始结构/性质。
- 属性值未重新执行 DFT；通过的是来源关联、结构标签一致性、字段范围与模板回填检查，不是实验真值或物理可实现性保证。
- 与 AtomWorldBench bench 的共享材料编号已标记但没有自动剔除，因此不要将联合训练后的评估称为材料级未见评估。
- 固定种子 20260910；对称性容差 0.1 Å，角度容差 5°，所有记录一致，不逐条调参。
- 构建脚本：`../build_matterchat_corpus.py`；重建必须指定不存在的输出目录，例如 `python ../build_matterchat_corpus.py --output ../llm_corpus_rebuild`，不会覆盖已有语料。

本次共生成 1821002 条问答；逐条回读检查、模板频率平衡检查、结构导出检查和 preview 子集检查均通过。

## 独立 CIF 文件

- `cif/train/`：128609 个；`cif/val/`：14290 个；`cif/gnome/`：15483 个，共 158382 个结构文件。
- 文件路径为 `cif/{split}/{structure_id}.cif`，例如 `cif/train/mp-149.cif`；同一结构的多条问答共用同一个 CIF，无需复制。
- `cif/index.jsonl` 给出结构 ID、划分、相对 CIF 路径、来源几何哈希和 CIF 文件哈希；其中路径相对于 `cif/` 目录。
- `cif/report.json` 记录全量导出和回读核对结果；所有文件均重新读取并核对原子数、元素/占位、晶胞度量及逐原子的周期位置。
- CIF 使用 P1 全位点写法，不进行对称性约简或晶胞精修。这只是存储方式，不表示材料的真实最高空间群是 P1；真实空间群应从几何结构识别。
- 原晶格的长度/夹角及所有位点保留，CIF 不编码原笛卡尔坐标系的整体朝向；所有源晶胞均已核实为右手系。问答内容和 `structures.jsonl` 保持不变，train/val 仅新增路径字段。
- 导出脚本是 `../export_matterchat_cifs.py`；重新导出应指定不存在的输出目录，不覆盖现有 CIF。
- CIF 导出完成后，在本目录运行 `python ../build_matterchat_corpus.py --attach-cif-paths` 可给 train/val 写入路径，并同步 preview 和报告。该步骤核对文件存在性、划分、结构 ID、来源几何哈希及全部原有字段，不重做语料生成。
