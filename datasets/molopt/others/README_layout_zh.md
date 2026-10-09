# 可搬迁的 LLM corpus 目录

本次只整理文件和路径，没有重新生成问答、修改性质标签、结构坐标、光谱数组、记录顺序或数据划分。

## 使用方法

- `messages/` 中的 JSONL 是实际语料。保留原有 train、val、validation、test、bench、gnome 文件名，不擅自合并。
- `structures/` 中是独立 CIF 或 XYZ；`spectra/` 中是光谱原文件。纯文本数据集对应目录可以为空。
- `others/` 是预览、模板、索引、审核材料和历史脚本，不是额外训练数据。
- 所有训练所需的结构和光谱路径都相对于 **llm_corpus 根目录**。读取 messages/train.jsonl 时，根目录是该文件的 parent.parent，而不是 messages 目录。
- 例如 cif_path 为 structures/ab/example.cif 时，实际路径为 corpus_root / cif_path。FG26 的 input_spectrum_refs 中 source_path 同样相对于 corpus_root。
- AtomWorldBench 沿用 metadata.input_cif、metadata.output_cif；它们现在指向包内 structures。metadata.path_base 的 .. 从新的 messages 目录出发也到达 corpus 根目录。
- 移动整个 llm_corpus 后不需要修改这些运行时相对路径。不要把路径、metadata、索引中的答案或目标结构当作输入问题。

## 哪些材料不是训练依赖

metadata 的原始数据库文件、审核证据、原 NPZ、原压缩包路径仅用于溯源，保留原始出处，不需要把整套原始库一起传输。FG26 结构输入直接用 XYZ，不需要原 NPZ。
FG26 官方 parquet 原样复制，行组、行偏移、key 和数组哈希不变。源文件名中的 train/test 不是本语料的 train/val；只按 messages 的原划分和已有引用加载，不直接把全部 parquet 行纳入训练。

## 验收与历史文件

当前目录和哈希以 others/layout_manifest.json、others/asset_manifest.jsonl 为准。全部修改后的 JSONL 已与备份逐条比对，差异限于路径；每个被引用的资产文件已重新校验哈希。预览从当前 messages 中取回。
以前的 build_report、manifest、verification、README 和脚本保留在 others，描述整理前的构建过程，旧路径和旧文件哈希不能当成本次文件布局的结果。不要直接运行历史生成器覆盖当前语料。
整理前的被改写索引另存于 /mnt/e/Datasets/Scientific_LLM_Corpus_Layout_Backup_20260914/molopt/original_files，不塞进当前包重复传输；原始数据文件没有删除。
