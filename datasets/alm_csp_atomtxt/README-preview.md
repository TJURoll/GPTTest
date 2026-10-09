# alm_csp_atomtxt 格式预览

这是解压后的数据格式预览，**不是完整数据集**。

1 MiB 以内的普通文本、数据、说明和 schema 文件保留原始完整内容；更大的主语料 messages/*.jsonl 最多保留前 500 条完整且可解析的源记录，辅助 JSONL 最多保留前 5 条。较大 CSV/TSV 保存表头和前 5 个物理数据行，TXT 保存前 5 行。每行上限 1 MiB、每个预览文件上限 10 MiB；超限时保留此前完整记录并写明原因，不保存残缺 JSON。

结构资源最多 100 个，优先选择样例消息引用的文件，另外保留少量顺序样例。优先引用来自各主语料文件的前 5 条记录；扩大的主语料样例中的其他结构引用可能未包含，清单会逐项列出。Parquet 只保存 footer 行数和字段结构，不包含二进制表体或数据行。脚本文件仅作为数据保存，未执行。

完整来源数量、实际导出数量、选择方法、未包含资源汇总及缺少的结构引用见 [preview-manifest.json](preview-manifest.json)。

`others/` 中保留的原始说明、清单、报告和哈希描述完整来源包或历史导出；它们不是这个 GitHub 子集的数量或校验值。当前子集以 `preview-manifest.json` 为准，截取后的文件不能使用完整来源文件的哈希校验。

## 直接查看样例

化学式、晶系和空间群约束下的晶体结构生成。

| 主对话文件 | 完整来源物理行数 | 本仓库记录数 | 保存方式 |
| --- | ---: | ---: | --- |
| [messages/train.jsonl](messages/train.jsonl) | 105,698 | 500 | first500 |
| [messages/val.jsonl](messages/val.jsonl) | 11,705 | 500 | first500 |

结构资产：完整来源 112,485 个，本仓库保留 30 个。

原始格式说明：[others/README_layout_zh.md](others/README_layout_zh.md)；[others/README_zh.md](others/README_zh.md)。

原包提供的辅助预览：[others/preview.jsonl](others/preview.jsonl)；[others/preview.md](others/preview.md)（数量单独统计）。

结构格式样例：[structures/ff/ff012a55dbfeb64b5a2481ad50d013a5bfcf5649f67ef1dda398b5bad6a8aab5.cif](structures/ff/ff012a55dbfeb64b5a2481ad50d013a5bfcf5649f67ef1dda398b5bad6a8aab5.cif)。

### 一条真实记录

以下只调整缩进；字段和值来自上面第一个主对话文件的第一条记录。

```json
{
  "id": "alm.csp.mp_3d_2020-80723",
  "messages": [
    {
      "content": "Please provide a crystal structure for Dy2Re2Si2C that belongs to the monoclinic crystal system and space group C2/m.",
      "role": "user"
    },
    {
      "content": "Here is a structure for Dy2Re2Si2C with space group C2/m in the monoclinic crystal system.",
      "role": "assistant"
    }
  ],
  "metadata": {
    "constraint_evidence": {
      "angle_tolerance_deg": 5.0,
      "space_group_number": 12,
      "symprec_A": 0.01
    },
    "constraints": {
      "crystal_system": "monoclinic",
      "formula": "Dy2Re2Si2C",
      "space_group": "C2/m"
    },
    "dataset": "ALM",
    "parent": "mp_3d_2020",
    "provenance": {
      "output": {
        "geometry_group_id": "60bbdc9c9411ad15fd683cdf306d0346294bc56a47961b11ead78ae0861f3802",
        "method": {
          "family": "PBE",
          "formation_energy_reference": "MP legacy corrected formation energy",
          "hubbards": {},
          "is_compatible": true,
          "is_hubbard": false,
          "task_ids": [
            "mp-1025240",
            "mp-1158443",
            "mp-1254750",
            "mp-1398423",
            "mp-1751250"
          ]
        },
        "native_id": "mp-1025240",
        "native_row_index": 80723,
        "source_idx": 80723,
        "upstream_geometry_status": "serialization_rounding"
      }
    },
    "query_template_id": "query_04",
    "response_template_id": "response_04",
    "sampling_seed": 20260911,
    "selected_row_index": 89648,
    "selected_source_file": "/mnt/e/Datasets/Inorganic_Materials/ALM_dataset/mp_jarvis_selected/csp.parquet",
    "selection_version": "mp_jarvis_selected_20260911",
    "source_row_id": "mp_3d_2020-80723",
    "source_row_index": 90474,
    "template_group": "formula_crystal_system_space_group"
  },
  "output_cif_path": "structures/60/60bbdc9c9411ad15fd683cdf306d0346294bc56a47961b11ead78ae0861f3802.cif",
  "output_cif_relative_path": "structures/60/60bbdc9c9411ad15fd683cdf306d0346294bc56a47961b11ead78ae0861f3802.cif",
  "output_cif_sha256": "3618be54f48e89dcb555f1c143bf72a7e4907a9b9dca9aae7fb0e4b7a3d49e2a",
  "output_geometry_sha256": "60bbdc9c9411ad15fd683cdf306d0346294bc56a47961b11ead78ae0861f3802",
  "split": "train",
  "split_group_id": "60bbdc9c9411ad15fd683cdf306d0346294bc56a47961b11ead78ae0861f3802",
  "task": "csp"
}
```
