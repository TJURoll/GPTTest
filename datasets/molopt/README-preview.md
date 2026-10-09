# molopt 格式预览

这是解压后的数据格式预览，**不是完整数据集**。

1 MiB 以内的普通文本、数据、说明和 schema 文件保留原始完整内容；更大的主语料 messages/*.jsonl 最多保留前 500 条完整且可解析的源记录，辅助 JSONL 最多保留前 5 条。较大 CSV/TSV 保存表头和前 5 个物理数据行，TXT 保存前 5 行。每行上限 1 MiB、每个预览文件上限 10 MiB；超限时保留此前完整记录并写明原因，不保存残缺 JSON。

结构资源最多 100 个，优先选择样例消息引用的文件，另外保留少量顺序样例。优先引用来自各主语料文件的前 5 条记录；扩大的主语料样例中的其他结构引用可能未包含，清单会逐项列出。Parquet 只保存 footer 行数和字段结构，不包含二进制表体或数据行。脚本文件仅作为数据保存，未执行。

完整来源数量、实际导出数量、选择方法、未包含资源汇总及缺少的结构引用见 [preview-manifest.json](preview-manifest.json)。

`others/` 中保留的原始说明、清单、报告和哈希描述完整来源包或历史导出；它们不是这个 GitHub 子集的数量或校验值。当前子集以 `preview-manifest.json` 为准，截取后的文件不能使用完整来源文件的哈希校验。

## 直接查看样例

按 QED、HBD、HBA 等约束编辑 SMILES。

| 主对话文件 | 完整来源物理行数 | 本仓库记录数 | 保存方式 |
| --- | ---: | ---: | --- |
| [messages/train.jsonl](messages/train.jsonl) | 340,294 | 500 | first500 |
| [messages/val.jsonl](messages/val.jsonl) | 19,624 | 500 | first500 |

结构资产：完整来源 0 个，本仓库保留 0 个。

原始格式说明：[others/README_layout_zh.md](others/README_layout_zh.md)；[others/README_zh.md](others/README_zh.md)。

原包提供的辅助预览：[others/preview.jsonl](others/preview.jsonl)；[others/preview.md](others/preview.md)（数量单独统计）。

### 一条真实记录

以下只调整缩进；字段和值来自上面第一个主对话文件的第一条记录。

```json
{
  "id": "MolOpt-Instructions:train-00000-of-00002-89f2b0767d199a7b:0",
  "messages": [
    {
      "role": "user",
      "content": "Given a molecule expressed in SMILES string, help me optimize it according to my requirements.\n\nCan you guide me in altering the molecule Cc1ccc2ccccc2c1CN(C)[C@H]1CCN(C(=O)c2ncc[nH]2)C1 to include the same hydrogen bond donors while ensuring the output molecule stays similar to the input molecule? Please inform me of the number of hydrogen bond donor(s) of the optimized molecule."
    },
    {
      "role": "assistant",
      "content": "After optimization based on your preferences, the molecule is represented by \"CN(Cc1c(-c2ccc(Cl)c(Cl)c2)ccc2ccccc12)[C@H]1CCN(C(=O)c2ncc[nH]2)C1\" with an approximate hydrogen bond donor(s) of 1."
    }
  ],
  "metadata": {
    "dataset": "MolOpt-Instructions_DrugAssist",
    "split": "train",
    "direction": "same",
    "failure_reasons": [],
    "input_molecule_sha256": "56c277e891efb11bf1982349a9dcd9f41cd8794af27952ae4b9d5fee8571e842",
    "input_smiles": "Cc1ccc2ccccc2c1CN(C)[C@H]1CCN(C(=O)c2ncc[nH]2)C1",
    "input_value": 1,
    "minimum_change": null,
    "output_molecule_sha256": "fc23405326ee0670ff6b2ae46a562e7a708936e671d7780a0ef4af261239068e",
    "output_smiles": "CN(Cc1c(-c2ccc(Cl)c(Cl)c2)ccc2ccccc12)[C@H]1CCN(C(=O)c2ncc[nH]2)C1",
    "output_value": 1,
    "pair_sha256": "d5738882d52e88d73cbd0eba1498c77fc547da2c1afbf80aa131227147b95151",
    "property_change": 0,
    "query_template_id": "HBD_012",
    "report_required": true,
    "reported_value": 1.0,
    "reported_value_text": "1",
    "response_template_id": "R_03",
    "review_reasons": [],
    "similarity": 0.7183098591549296,
    "similarity_required": true,
    "source": {
      "file": "data/train-00000-of-00002-89f2b0767d199a7b.parquet",
      "row_index": 0,
      "split": "train"
    },
    "source_record_sha256": "ebe5fe318ffc9a877393373c677b3d3761c660527ead886de1f8633954575ac4",
    "split_overlap_flags": [],
    "status": "accepted",
    "structure_requirement": "similar",
    "task": "HBD"
  }
}
```
