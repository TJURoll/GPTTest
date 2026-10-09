# MolOpt QED / HBD / HBA LLM Corpus

仅将 screened_qed_hbd_hba 中通过筛选的原始分子编辑配对转为单轮 SFT 对话。
本次不再生成、扩写或随机抽取模板，不修改英文、SMILES 或回答数值。

## 使用哪个文件

- train.jsonl：训练，340294 条。
- val.jsonl：验证，19624 条。
- preview.jsonl：12 条真实预览，来自最终文件，不是另外生成的样例。
- manifest.json：完整计数、模板使用量、来源、哈希、筛选规则和验证结果。

## 每条记录

- id：原始任务文件名和零起始行号构成的唯一标识。
- messages[0]：user，原 instruction + 两个换行 + 原 input。
- messages[1]：assistant，原 output。
- metadata：数据集、split、任务、全部 screening 校验信息及原始来源。

只将 messages 作为语言模型对话；metadata 是筛选和追溯信息，不要拼入 prompt。
不添加 system prompt，不添加 CIF、三维坐标或新的结构占位符。
和现有 ChEBI-20 corpus 一样，SMILES 字符串保留在对话中。

## 边界与划分

总计 359918 条，一条通过筛选的记录对应一条语料，不扩增。
原始数据、screened_qed_hbd_hba、discarded 和 review 均未改动。
未把未通过、待核验、其他分子任务或通用指令加入 corpus。
本次只做格式转换，未新增性质计算、物理合理性判定或药理推断。

沿用原 train/val，不自动去重或重划分。
两个 split 仍共享 1 组无方向分子对和 37 个分子身份。
训练记录的 metadata.split_overlap_flags 保留相关标记。
因此不能把本 val 宣称为分子身份完全独立的评估；按后续用途决定是否排除共享身份。
原 test.txt / test_500.txt 仅有输入 SMILES，未转换成带答案的 test.jsonl，也未完成与其的身份隔离。

## 验证与复现

所有输出逐条回读，与筛选来源的指令、答案、SMILES、元数据和顺序严格比较。
验证全局 ID 唯一、预览为最终语料的逐字子集、来源文件哈希未变。
再次运行 build_llm_corpus.py 时须指定一个新的 --output，脚本拒绝覆盖已有目录。
