# matterchat 格式预览

这是解压后的数据格式预览，**不是完整数据集**。

1 MiB 以内的普通文本、数据、说明和 schema 文件保留原始完整内容；更大的主语料 messages/*.jsonl 最多保留前 500 条完整且可解析的源记录，辅助 JSONL 最多保留前 5 条。较大 CSV/TSV 保存表头和前 5 个物理数据行，TXT 保存前 5 行。每行上限 1 MiB、每个预览文件上限 10 MiB；超限时保留此前完整记录并写明原因，不保存残缺 JSON。

结构资源最多 100 个，优先选择样例消息引用的文件，另外保留少量顺序样例。优先引用来自各主语料文件的前 5 条记录；扩大的主语料样例中的其他结构引用可能未包含，清单会逐项列出。Parquet 只保存 footer 行数和字段结构，不包含二进制表体或数据行。脚本文件仅作为数据保存，未执行。

完整来源数量、实际导出数量、选择方法、未包含资源汇总及缺少的结构引用见 [preview-manifest.json](preview-manifest.json)。

`others/` 中保留的原始说明、清单、报告和哈希描述完整来源包或历史导出；它们不是这个 GitHub 子集的数量或校验值。当前子集以 `preview-manifest.json` 为准，截取后的文件不能使用完整来源文件的哈希校验。

## 直接查看样例

材料性质问答，另含 gnome 外部评测划分。

| 主对话文件 | 完整来源物理行数 | 本仓库记录数 | 保存方式 |
| --- | ---: | ---: | --- |
| [messages/gnome.jsonl](messages/gnome.jsonl) | 177,922 | 500 | first500 |
| [messages/train.jsonl](messages/train.jsonl) | 1,478,871 | 500 | first500 |
| [messages/val.jsonl](messages/val.jsonl) | 164,209 | 500 | first500 |

结构资产：完整来源 158,382 个，本仓库保留 35 个。

原始格式说明：[others/README.md](others/README.md)；[others/README_layout_zh.md](others/README_layout_zh.md)。

原包提供的辅助预览：[others/preview.jsonl](others/preview.jsonl)；[others/preview.md](others/preview.md)（数量单独统计）。

结构格式样例：[structures/val/mp-100.cif](structures/val/mp-100.cif)。

### 一条真实记录

以下只调整缩进；字段和值来自上面第一个主对话文件的第一条记录。

```json
{
  "structure_id": "mp-3216103",
  "messages": [
    {
      "role": "user",
      "content": "What is the chemical formula for this material?"
    },
    {
      "role": "assistant",
      "content": "This material has the reduced formula CaAu2(SO4)4."
    }
  ],
  "metadata": {
    "split": "gnome",
    "source_file": "Material_data_GnoME_processed_mace.pkl",
    "task": "reduced_formula",
    "subgroup": "reduced_formula",
    "question_pool": "formula",
    "question_index": 0,
    "response_index": 1,
    "geometry_sha256": "6cdf0a1843032c561e190079cf79b671d6f24f94d18f6cbe0f0392019beac77c",
    "derived_fields": [
      "reduced_formula",
      "crystal_system"
    ],
    "atomworldbench_bench_shared_mp_id": false
  },
  "cif_path": "structures/gnome/mp-3216103.cif"
}
```
