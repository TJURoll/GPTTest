# hmof 格式预览

这是解压后的数据格式预览，**不是完整数据集**。

1 MiB 以内的普通文本、数据、说明和 schema 文件保留原始完整内容；更大的主语料 messages/*.jsonl 最多保留前 500 条完整且可解析的源记录，辅助 JSONL 最多保留前 5 条。较大 CSV/TSV 保存表头和前 5 个物理数据行，TXT 保存前 5 行。每行上限 1 MiB、每个预览文件上限 10 MiB；超限时保留此前完整记录并写明原因，不保存残缺 JSON。

结构资源最多 100 个，优先选择样例消息引用的文件，另外保留少量顺序样例。优先引用来自各主语料文件的前 5 条记录；扩大的主语料样例中的其他结构引用可能未包含，清单会逐项列出。Parquet 只保存 footer 行数和字段结构，不包含二进制表体或数据行。脚本文件仅作为数据保存，未执行。

完整来源数量、实际导出数量、选择方法、未包含资源汇总及缺少的结构引用见 [preview-manifest.json](preview-manifest.json)。

`others/` 中保留的原始说明、清单、报告和哈希描述完整来源包或历史导出；它们不是这个 GitHub 子集的数量或校验值。当前子集以 `preview-manifest.json` 为准，截取后的文件不能使用完整来源文件的哈希校验。

## 直接查看样例

MOF 吸附、孔径、空隙率和表面积等性质问答。

| 主对话文件 | 完整来源物理行数 | 本仓库记录数 | 保存方式 |
| --- | ---: | ---: | --- |
| [messages/train.jsonl](messages/train.jsonl) | 534,879 | 500 | first500 |
| [messages/val.jsonl](messages/val.jsonl) | 28,153 | 500 | first500 |

结构资产：完整来源 70,634 个，本仓库保留 30 个。

原始格式说明：[others/README_layout_zh.md](others/README_layout_zh.md)；[others/README_zh.md](others/README_zh.md)。

原包提供的辅助预览：[others/preview.jsonl](others/preview.jsonl)；[others/preview.md](others/preview.md)（数量单独统计）。

结构格式样例：[structures/ff/hMOF-1000609.cif](structures/ff/hMOF-1000609.cif)。

### 一条真实记录

以下只调整缩进；字段和值来自上面第一个主对话文件的第一条记录。

```json
{
  "id": "hMOF-28040:co2_five_points",
  "hmof_id": "hMOF-28040",
  "structure_group_id": "hmof-geometry-28040",
  "task": "co2_uptake",
  "template_group": "co2_five_points",
  "split": "train",
  "cif_path": "structures/3d/hMOF-28040.cif",
  "cif_relative_path": "structures/3d/hMOF-28040.cif",
  "cif_sha256": "3d6e1be816ccdd8ca5bf71794f7a73be953b71609fd1831e1e0e1a79cd43fd70",
  "geometry_sha256": "acf395efa5c104ec78541d5efecfcafc93adadc2259a3620b747c663411f8a94",
  "messages": [
    {
      "role": "user",
      "content": "List the five pressure-uptake pairs for pure CO2 adsorption in this material at 298 K, using pressures of 0.01, 0.05, 0.1, 0.5, and 2.5 bar and uptake in mol/kg."
    },
    {
      "role": "assistant",
      "content": "This framework's pure CO2 uptake at 298 K is 0.0337331 mol/kg at 0.01 bar; 0.191154 mol/kg at 0.05 bar; 0.365783 mol/kg at 0.1 bar; 1.96078 mol/kg at 0.5 bar; and 9.21937 mol/kg at 2.5 bar."
    }
  ],
  "metadata": {
    "status": "corpus",
    "query_style": "explicit",
    "query_template_id": "CO2C_E03",
    "response_template_id": "CO2C_R04",
    "sampling_seed": 20260914,
    "source_split": "LLM4Mat-Bench/hmof/train",
    "source_hmof_ids": [
      "hMOF-28040"
    ],
    "forced_train_by_qmof_overlap": false,
    "potential_qmof_overlap": [],
    "answer_schema_reference": "others/provenance/task_schema.json",
    "template_bank_reference": "others/provenance/templates.json",
    "answer_values": {
      "co2_uptake": {
        "adsorbate": "CO2",
        "temperature_kelvin": 298.0,
        "adsorption_basis": "absolute",
        "pressures_bar": [
          0.01,
          0.05,
          0.1,
          0.5,
          2.5
        ],
        "uptake_mol_per_kg": [
          0.0337331,
          0.191154,
          0.365783,
          1.96078,
          9.21937
        ]
      }
    },
    "source_isotherm_id": 5133090,
    "rendered_parameters": {
      "uptake_0p01": "0.0337331",
      "uptake_0p05": "0.191154",
      "uptake_0p1": "0.365783",
      "uptake_0p5": "1.96078",
      "uptake_2p5": "9.21937"
    }
  }
}
```
