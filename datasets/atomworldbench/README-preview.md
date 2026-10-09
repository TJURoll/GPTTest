# atomworldbench 格式预览

这是解压后的数据格式预览，**不是完整数据集**。

1 MiB 以内的普通文本、数据、说明和 schema 文件保留原始完整内容；更大的主语料 messages/*.jsonl 最多保留前 500 条完整且可解析的源记录，辅助 JSONL 最多保留前 5 条。较大 CSV/TSV 保存表头和前 5 个物理数据行，TXT 保存前 5 行。每行上限 1 MiB、每个预览文件上限 10 MiB；超限时保留此前完整记录并写明原因，不保存残缺 JSON。

结构资源最多 100 个，优先选择样例消息引用的文件，另外保留少量顺序样例。优先引用来自各主语料文件的前 5 条记录；扩大的主语料样例中的其他结构引用可能未包含，清单会逐项列出。Parquet 只保存 footer 行数和字段结构，不包含二进制表体或数据行。脚本文件仅作为数据保存，未执行。

完整来源数量、实际导出数量、选择方法、未包含资源汇总及缺少的结构引用见 [preview-manifest.json](preview-manifest.json)。

`others/` 中保留的原始说明、清单、报告和哈希描述完整来源包或历史导出；它们不是这个 GitHub 子集的数量或校验值。当前子集以 `preview-manifest.json` 为准，截取后的文件不能使用完整来源文件的哈希校验。

## 直接查看样例

晶体原子编辑任务，另含 bench 评测划分。

| 主对话文件 | 完整来源物理行数 | 本仓库记录数 | 保存方式 |
| --- | ---: | ---: | --- |
| [messages/bench.jsonl](messages/bench.jsonl) | 9,424 | 500 | first500 |
| [messages/train.jsonl](messages/train.jsonl) | 57,452 | 500 | first500 |

结构资产：完整来源 133,752 个，本仓库保留 40 个。

原始格式说明：[others/README_layout_zh.md](others/README_layout_zh.md)；[others/README_zh.md](others/README_zh.md)。

原包提供的辅助预览：[others/preview.jsonl](others/preview.jsonl)；[others/preview.md](others/preview.md)（数量单独统计）。

结构格式样例：[structures/train/SwapAtomsAction/output/000000_56505161-b7c3-4e0a-9813-30fa5ad68e6f.cif](structures/train/SwapAtomsAction/output/000000_56505161-b7c3-4e0a-9813-30fa5ad68e6f.cif)。

### 一条真实记录

以下只调整缩进；字段和值来自上面第一个主对话文件的第一条记录。

```json
{
  "id": "AtomWorldBench:bench:AddAtomAction:6d9e7bf9-1738-4808-99ac-a9390f8a7e37",
  "messages": [
    {
      "role": "user",
      "content": "Add one Ba atom at the Cartesian coordinate [6.5465 4.7379 3.9022] to the structure."
    },
    {
      "role": "assistant",
      "content": "One Ba atom has been added at the Cartesian coordinates [6.5465 4.7379 3.9022] angstrom."
    }
  ],
  "metadata": {
    "split": "bench",
    "action_type": "AddAtomAction",
    "problem_id": "6d9e7bf9-1738-4808-99ac-a9390f8a7e37",
    "mp_id": "mp-1013842",
    "source_file": "/mnt/e/Datasets/Inorganic_Materials/AtomWorldBench/bench/AddAtomAction.json",
    "source_record_index": 0,
    "original_source_file": "/mnt/e/Datasets/Inorganic_Materials/AtomWorldBench/original_backup_20260909/bench/AddAtomAction.json",
    "original_source_record_index": 0,
    "input_sha256": "3b04bf73698f99e8a4c4d40dd0e7717cb6728f526dd52653dff68a6a1758be17",
    "output_sha256": "762167900339b0d0da71b927bb9ac3989f985bc01a46e88dc6568044c779e93e",
    "dataset": "AtomWorldBench",
    "template_id": null,
    "template_group": null,
    "user_text_policy": "original_instruction_format_neutralized",
    "response_template_id": "01.1",
    "response_type": "ACTION-SPECIFIC",
    "source_prompt_group": "01",
    "original_prompt": "Add one Ba atom at the Cartesian coordinate [6.5465 4.7379 3.9022] to the cif file.",
    "parameters": {
      "element": "Ba",
      "cartesian_coordinate": "[6.5465 4.7379 3.9022]"
    },
    "path_base": "..",
    "input_cif": "structures/bench/AddAtomAction/input/000000_6d9e7bf9-1738-4808-99ac-a9390f8a7e37.cif",
    "output_cif": "structures/bench/AddAtomAction/output/000000_6d9e7bf9-1738-4808-99ac-a9390f8a7e37.cif",
    "has_cif_metadata_warning": true
  }
}
```
