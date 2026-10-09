# MOF_papers 可搬迁语料

## 目录

- messages/data.jsonl 保存 101,991 条原有问答。本数据集没有 train/val/test 划分，本次不新增划分。
- structures/ 保存 13,302 个 CIF，保持论文子目录与原文件名；文件字节不变，没有重写坐标。
- spectra/ 为空，本数据集没有独立光谱输入文件。
- others/ 保存预览、来源索引、历史摘要和当前目录验收报告。

## 路径与加载

每条记录的 cif_path 相对于 llm_corpus 根目录。例如读取 messages/data.jsonl 后，用 corpus_root / sample['cif_path'] 加载结构，不是从 messages/ 下直接拼接。
messages 中的问答、qa_id、条目顺序保持不变，仅将 cifs/ 前缀改为 structures/。
数据仍是未经 train/val/test 划分的统一语料；后续不能把同一论文或同一结构的不同问答随意分到训练和验证两侧。

## 其他文件

others/preview.json 与 preview.md 展示本次 messages 中的同一批样本，路径已经同步。
others/provenance.jsonl 保留 13,801 条结构来源记录，其中 499 条为零 QA，仅保留来源记录，不增加训练样本或复制无用结构。
provenance 的 records_sha256 已更新为当前 data.jsonl 中对应结构各行原始字节的 SHA256，包含换行；source_records_sha256 保留迁移前的校验和。其余源文件哈希保持原值。
qa_source_path 和 cif_source_path 是相对于原 MOF_papers 目录的历史来源位置，不是训练加载依赖。训练不需要随包复制原论文、PDF、模型原始输出或原始筛选工作目录。
summary.json 和 README.md 是历史导出记录，旧文件名与旧文件哈希不代表当前布局。当前文件与资产校验和见 layout_manifest.json、asset_manifest.jsonl；逐结构问答核验见 record_group_verification.json。
这次只整理目录、路径和派生校验和，不改科学答案，也不把文件一致性校验当成新的科学真实性认证。
