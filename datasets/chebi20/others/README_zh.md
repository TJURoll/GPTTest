# ChEBI-20 LLM 训练语料

按父目录 `template.txt` 的六种英文 Query 构造 SMILES → description 的单轮对话式 SFT 语料。

## 文件与用途

| 文件 | 条数 | 用途 |
|---|---:|---|
| train.jsonl | 26,407 | 训练 |
| validation.jsonl | 3,301 | 验证 |
| test.jsonl | 3,300 | 测试 |
| manifest.json | — | 模板、比例、随机种子、条数、来源及输出 SHA-256、验证结果 |

原始三个 split 分别转换，不混合。每条原始记录仅生成一条语料，六个模板作为替代表述分配，不做六倍扩增。每个 split 内仍保留原始记录顺序。

## 每行格式

每行是一个 JSON 对象：

- `id`：`ChEBI-20:<CID>`。
- `messages[0]`：`role=user`，`content` 为原模板 Query、两个换行、原始 SMILES。
- `messages[1]`：`role=assistant`，`content` 为原始 description。
- `metadata`：数据集名、split、CID、模板 ID、源文件名、从 0 开始的数据记录索引。

训练时使用 `messages`；`id` 和 `metadata` 用于追溯。没有额外添加 system prompt、推理解释或新的性质标签。SMILES 和 description 按原文本保留，JSON 中反斜杠等字符的转义解码后与原字段一致。

## 模板比例

模板文件中六个权重都是 16.67%，合计 100.02%。转换时归一化为每种 1/6，按最大余数法分配整数条数，再以固定随机种子 20260909 在各 split 内打乱模板分配。

| 模板 ID | train | validation | test |
|---|---:|---:|---:|
| 1 | 4,402 | 551 | 550 |
| 2 | 4,401 | 550 | 550 |
| 3 | 4,401 | 550 | 550 |
| 4 | 4,401 | 550 | 550 |
| 5 | 4,401 | 550 | 550 |
| 6 | 4,401 | 550 | 550 |

## 验证及复现

构建脚本逐条回读全部输出，验证模板、原 SMILES、原 description、角色、CID 和来源信息；检查记录数量、模板配额、跨 split CID 唯一性及源文件哈希未变。

```bash
python /mnt/e/Datasets/Molecules/ChEBI-20/build_llm_corpus.py
```

只使用 Python 标准库。重跑会重新生成 `llm_corpus` 中的 JSONL 和 manifest，保留原始 TXT。变更模板或参数后，应以新 manifest 的统计为准。

本次操作是按模板转换语料，没有新增语义清洗或把原始描述重新认定为已证实事实。
