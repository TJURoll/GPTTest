# alm_polymorph 格式预览

这是解压后的数据格式预览，**不是完整数据集**。

1 MiB 以内的普通文本、数据、说明和 schema 文件保留原始完整内容；更大的主语料 messages/*.jsonl 最多保留前 500 条完整且可解析的源记录，辅助 JSONL 最多保留前 5 条。较大 CSV/TSV 保存表头和前 5 个物理数据行，TXT 保存前 5 行。每行上限 1 MiB、每个预览文件上限 10 MiB；超限时保留此前完整记录并写明原因，不保存残缺 JSON。

结构资源最多 100 个，优先选择样例消息引用的文件，另外保留少量顺序样例。优先引用来自各主语料文件的前 5 条记录；扩大的主语料样例中的其他结构引用可能未包含，清单会逐项列出。Parquet 只保存 footer 行数和字段结构，不包含二进制表体或数据行。脚本文件仅作为数据保存，未执行。

完整来源数量、实际导出数量、选择方法、未包含资源汇总及缺少的结构引用见 [preview-manifest.json](preview-manifest.json)。

`others/` 中保留的原始说明、清单、报告和哈希描述完整来源包或历史导出；它们不是这个 GitHub 子集的数量或校验值。当前子集以 `preview-manifest.json` 为准，截取后的文件不能使用完整来源文件的哈希校验。

## 直接查看样例

相同组分的多晶型结构转换，含结构对和能量信息。

| 主对话文件 | 完整来源物理行数 | 本仓库记录数 | 保存方式 |
| --- | ---: | ---: | --- |
| [messages/train.jsonl](messages/train.jsonl) | 13,677 | 500 | first500 |
| [messages/val.jsonl](messages/val.jsonl) | 669 | 500 | first500 |

结构资产：完整来源 10,922 个，本仓库保留 40 个。

原始格式说明：[others/README_layout_zh.md](others/README_layout_zh.md)；[others/README_zh.md](others/README_zh.md)。

原包提供的辅助预览：[others/preview.jsonl](others/preview.jsonl)；[others/preview.md](others/preview.md)（数量单独统计）。

结构格式样例：[structures/ff/ff0be0d8e2d78ff0a6866e0963612afb50dd68ff5eed36b3a54623212b94911f.cif](structures/ff/ff0be0d8e2d78ff0a6866e0963612afb50dd68ff5eed36b3a54623212b94911f.cif)。

### 一条真实记录

以下只调整缩进；字段和值来自上面第一个主对话文件的第一条记录。

```json
{
  "id": "alm.polymorph.9540",
  "input_cif_path": "structures/a8/a8cc9f51786e90556be6c76cf291f21b11403c9563cdc8733fae6b5c682ff9a9.cif",
  "input_cif_relative_path": "structures/a8/a8cc9f51786e90556be6c76cf291f21b11403c9563cdc8733fae6b5c682ff9a9.cif",
  "input_cif_sha256": "54aa959f66300add92a824d84fbd1fcf3253c535327aa9b64fae3c8b35ff47b3",
  "input_geometry_sha256": "a8cc9f51786e90556be6c76cf291f21b11403c9563cdc8733fae6b5c682ff9a9",
  "input_native_id": "mp-1191044",
  "messages": [
    {
      "content": "Provide an alternative polymorph of this crystal.",
      "role": "user"
    },
    {
      "content": "Here is another polymorph that preserves the input structure's composition.",
      "role": "assistant"
    }
  ],
  "metadata": {
    "audit_file": "/mnt/e/Datasets/Inorganic_Materials/ALM_dataset/polymorph_checked/pair_checks.parquet",
    "constraints": {
      "different_polymorph": true,
      "lower_energy_above_hull": false,
      "same_composition": true
    },
    "dataset": "ALM",
    "energy": {
      "field": "e_above_hull",
      "input": {
        "e_above_hull": 0.23104984681817786,
        "energy_per_atom": -4.124841209545455,
        "formation_energy_per_atom": -0.1683750306890908
      },
      "orientation": "current_input_output",
      "output": {
        "e_above_hull": 0.07385704848484487,
        "energy_per_atom": -4.282034007878788,
        "formation_energy_per_atom": -0.32556782902242426
      },
      "output_minus_input": {
        "e_above_hull": -0.157192798333333,
        "energy_per_atom": -0.157192798333333,
        "formation_energy_per_atom": -0.15719279833333347
      },
      "unit": "eV/atom",
      "used_as_query_condition": false
    },
    "is_reversed": false,
    "parent": "mp_3d_2020",
    "provenance": {
      "input": {
        "current_deprecation_checked": false,
        "endpoint_id": "799813edf40a4c7cb032c0d564ff22f6a0d55a88f772a518b6bd3e2c53643438",
        "method": {
          "family": "PBE",
          "formation_energy_reference": "MP legacy corrected formation energy",
          "hubbards": {},
          "is_compatible": true,
          "is_hubbard": false,
          "task_ids": [
            "mp-1191044",
            "mp-1191208",
            "mp-1347769"
          ]
        },
        "native_geometry_bound": true,
        "native_id": "mp-1191044",
        "native_row_index": 91884
      },
      "output": {
        "current_deprecation_checked": false,
        "endpoint_id": "53b905bcc202955507658e54c188d0cb380a7aabc60b5ff8e9046bdc58cca71b",
        "method": {
          "family": "PBE",
          "formation_energy_reference": "MP legacy corrected formation energy",
          "hubbards": {},
          "is_compatible": true,
          "is_hubbard": false,
          "task_ids": [
            "mp-1182236",
            "mp-1340754",
            "mp-1685625"
          ]
        },
        "native_geometry_bound": true,
        "native_id": "mp-1182236",
        "native_row_index": 80802
      }
    },
    "query_template_id": "query_04",
    "response_template_id": "response_04",
    "sampling_seed": 20260913,
    "selection_file": "/mnt/e/Datasets/Inorganic_Materials/ALM_dataset/polymorph_checked/accepted_pairs.parquet",
    "source_audit_orientation": "original",
    "source_file": "/mnt/e/Datasets/Inorganic_Materials/ALM_dataset/alm_bench/polymorph.parquet",
    "source_row_id": "polymorph_under_hull-mp-mp-1191044-to-mp-1182236-ehull_0.2310_to_0.0738-n_uniq_3",
    "source_row_index": 9540,
    "split_origin": "inherit_train",
    "template_group": "same_composition_distinct_polymorph",
    "unordered_pair_id": "609beaaa52e87809aa2d3155d8b4b2817618fdf41328dc341f9c8f1411833b28"
  },
  "output_cif_path": "structures/e6/e6bb695c4ebf43b1ebf9010c759aef4cc41ba2d71a0b00fe2c6499dabd099418.cif",
  "output_cif_relative_path": "structures/e6/e6bb695c4ebf43b1ebf9010c759aef4cc41ba2d71a0b00fe2c6499dabd099418.cif",
  "output_cif_sha256": "311ef23956d3d38669036cb152c1b11a2ffcf4bcadf08fa6b78a16f852a2c275",
  "output_geometry_sha256": "e6bb695c4ebf43b1ebf9010c759aef4cc41ba2d71a0b00fe2c6499dabd099418",
  "output_native_id": "mp-1182236",
  "split": "train",
  "split_group_id": "1cf8a64c50f04cb1b72c8177849931b1a74c4f4adbe3a63617fe90b7dc543964",
  "task": "polymorph"
}
```
