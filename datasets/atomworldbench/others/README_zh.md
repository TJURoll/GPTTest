# AtomWorldBench 指令编辑 LLM 语料

## 文件

- train.jsonl：57,452 条，12 种动作，80 条启用 user 模板、52 条回复模板。
- bench.jsonl：9,424 条，原始指令仅替换文件格式称呼，不随机扩写、不混入训练；回复固定为对应动作的第一条专属模板。
- preview.jsonl：train 中的 105 条预览，覆盖 80 条 user 与 52 条回复模板；不是额外训练数据，不要重复拼入 train。
- manifest.json：随机种子、来源/产物 SHA256、模板快照信息和实际分配数量。
- templates_snapshot.txt：本次使用的用户模板文件原样快照，含禁用分组标记。
- response_templates_snapshot.txt：本次使用的回复模板文件原样快照。
- split_overlap_report.json：跨划分 ID、mp_id、CIF 文本哈希和任务参数重复统计；只报告，不自动删除数据。

## 对话与独立结构输入输出

只有 user 和 assistant 两条消息，没有 system 消息。
user 只有填好原始参数的动作指令；assistant 只有填好原始参数的独立回复。
两条消息都不包含 CIF 格式名称、Input CIF 标签、结构占位符、未填参数槽位、文件路径或结构正文。
只限制 messages：metadata 的原始指令、路径字段以及原样模板快照可以保留源文件格式名称，用于追溯；不要将这些内容拼进模型消息。

这是供自定义结构加载/输出流程使用的索引语料；输入输出结构由独立模态或字段提供，不能仅以文字确认替代结构监督。
输入文件定位：语料目录 / metadata.path_base / metadata.input_cif。
输出文件定位：语料目录 / metadata.path_base / metadata.output_cif。
默认 path_base 为 ..，路径最终指向现有 cif_pairs 中的文件；没有复制或改写 CIF。
source_file、original_source_file 也相对于 path_base；对应行索引从 0 开始。
metadata.parameters 保存原始参数字符串，包括向量内空格和数值精度。加载输入结构时必须保留原始原子顺序，索引从 0 开始。
metadata.response_template_id 和 response_type 记录回复来源；原始指令保存在 original_prompt 中。

## 抽样规则

每条原始记录只生成一条语料，不做五倍扩增，也不改变各动作样本数。
在同一动作、同一子组的五条模板中等比例分配，数量最多相差一条，再按固定种子 20260909 打乱模板分配。
原有数据行顺序保留。SuperCell 按原始分隔符分组。Including、MoveAround 和 bench wording 不进入训练模板池。
训练回复 GENERAL 为 14,363 条，ACTION-SPECIFIC 为 43,089 条，目标比例为 25%/75%。全局通用条数取四分之一最近整数，再按动作最大余数分配，动作内随机选择记录。
GENERAL 共用四条模板；ACTION-SPECIFIC 按对应动作使用四条模板，SuperCell 的五个 user 子组合用一套回复。每个回复池内配额最多相差一条。
user 模板、回复类型和回复措辞使用独立随机流，不固定绑定。具体计数见 manifest.json 的 train_template_quotas、train_response_quotas。
bench 的 template_id/template_group 为 null，source_prompt_group 记录原始分组。原指令中的 cif file 仅改为 structure，操作和参数不变，格式归一化后的指令不是逐字原始 benchmark 提示。
bench 的 assistant 固定使用对应动作第一条专属回复，不参与训练集的 25%/75% 计数。

## 本次验证及限制

全部记录核对来源 ID、原始指令、参数提取/回填、模板分组、CIF 路径与源字符串哈希，输出 JSONL 全量读回比对。
实际读取并验证了 133,752 个活动 CIF 文件的 SHA256；源文件哈希在生成前后保持一致。
本次只做指令编辑语料转换，不新增物理合理性、元素或短距离过滤，不因这些条件删除记录；此前通过指令编辑核验的数据全部保留。
此前规则核验的适用范围见数据根目录 CLEANING_STATUS_zh.md；本次未重复执行全量几何计算。
有 6,015 条记录保留 CIF 元数据警告，metadata.has_cif_metadata_warning 标记这些记录；详情见根目录 audit_metadata_warnings.jsonl。
同 mp_id 不自动等于泄漏；CIF 哈希不同也不证明结构不同，未执行全量结构相似性排查。
bench 是筛选后的本地评估子集，不等同于完整官方 benchmark。没有创建新的 validation 或改变原有划分。

## 重现

在数据根目录运行：python build_llm_corpus.py --seed 20260909 --workers 16 --output-dir llm_corpus_rebuild
仅用 Python 标准库（Python 3.10+）；拒绝覆盖已有输出或 .pending 目录。
只有全部检查通过后才发布最终目录；失败时保留 .pending/failure.json，不能拿未完成的目录训练。
