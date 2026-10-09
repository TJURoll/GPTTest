# qmof 格式预览

这是解压后的数据格式预览，**不是完整数据集**。

1 MiB 以内的普通文本、数据、说明和 schema 文件保留原始完整内容；更大的主语料 messages/*.jsonl 最多保留前 500 条完整且可解析的源记录，辅助 JSONL 最多保留前 5 条。较大 CSV/TSV 保存表头和前 5 个物理数据行，TXT 保存前 5 行。每行上限 1 MiB、每个预览文件上限 10 MiB；超限时保留此前完整记录并写明原因，不保存残缺 JSON。

结构资源最多 100 个，优先选择样例消息引用的文件，另外保留少量顺序样例。优先引用来自各主语料文件的前 5 条记录；扩大的主语料样例中的其他结构引用可能未包含，清单会逐项列出。Parquet 只保存 footer 行数和字段结构，不包含二进制表体或数据行。脚本文件仅作为数据保存，未执行。

完整来源数量、实际导出数量、选择方法、未包含资源汇总及缺少的结构引用见 [preview-manifest.json](preview-manifest.json)。

`others/` 中保留的原始说明、清单、报告和哈希描述完整来源包或历史导出；它们不是这个 GitHub 子集的数量或校验值。当前子集以 `preview-manifest.json` 为准，截取后的文件不能使用完整来源文件的哈希校验。

## 直接查看样例

QMOF 材料性质问答。

| 主对话文件 | 完整来源物理行数 | 本仓库记录数 | 保存方式 |
| --- | ---: | ---: | --- |
| [messages/train.jsonl](messages/train.jsonl) | 311,695 | 500 | first500 |
| [messages/val.jsonl](messages/val.jsonl) | 34,629 | 500 | first500 |

结构资产：完整来源 20,372 个，本仓库保留 30 个。

原始格式说明：[others/README_layout_zh.md](others/README_layout_zh.md)；[others/README_zh.md](others/README_zh.md)。

原包提供的辅助预览：[others/preview.jsonl](others/preview.jsonl)；[others/preview.md](others/preview.md)（数量单独统计）。

结构格式样例：[structures/qmof-0000295.cif](structures/qmof-0000295.cif)。

### 一条真实记录

以下只调整缩进；字段和值来自上面第一个主对话文件的第一条记录。

```json
{
  "id": "qmof-61b7fa5:description",
  "qmof_id": "qmof-61b7fa5",
  "task": "description",
  "split": "train",
  "cif_path": "structures/qmof-61b7fa5.cif",
  "cif_relative_path": "structures/qmof-61b7fa5.cif",
  "geometry_sha256": "65e65a7791aceac45972b8d3fc1ebb9ee7e102fb44c72f73e4c9b118c0c0da9a",
  "messages": [
    {
      "role": "user",
      "content": "Can you describe this material?"
    },
    {
      "role": "assistant",
      "content": "The material has reduced chemical formula LiBC4F2H3NO4, with 64 atoms in the unit cell, and belongs to the orthorhombic crystal system. Its formation energy relative to the constituent elements in their reference states is -1.182326 eV/atom, and its energy above the convex hull is 0.191693 eV/atom."
    }
  ],
  "metadata": {
    "status": "corpus",
    "assigned_split": "train",
    "structure_group_id": "qmof-61b7fa5",
    "forced_train_by_overlap_group": false,
    "query_template_id": "Q01",
    "response_template_id": "R10",
    "answer_values": {
      "formula": "LiBC4F2H3NO4",
      "atom_count": 64,
      "crystal_system": "orthorhombic",
      "thermo.formation_energy": -1.1823259900651042,
      "thermo.energy_above_hull": 0.19169267697916847
    },
    "answer_sources": {
      "formula": {
        "title_zh": "化学式",
        "source_field": "info.formula_reduced",
        "unit": null,
        "geometry_method": "PBE-D3BJ",
        "enabled_for_corpus": true
      },
      "atom_count": {
        "title_zh": "晶胞原子数",
        "source_field": "info.natoms",
        "unit": "atoms/cell",
        "geometry_method": "PBE-D3BJ",
        "enabled_for_corpus": true
      },
      "crystal_system": {
        "title_zh": "晶系",
        "source_field": "info.symmetry.spacegroup_crystal",
        "unit": null,
        "geometry_method": "PBE-D3BJ",
        "enabled_for_corpus": true
      },
      "thermo.formation_energy": {
        "title_zh": "相对于元素的形成能",
        "source_field": "thermo.formation_energy",
        "unit": "eV/atom",
        "method": "QMOF-Thermo PBE-D3(BJ), published reference phases",
        "geometry_method": "PBE-D3BJ",
        "require_method_in_question_or_answer": false,
        "method_in_metadata": true,
        "enabled_for_corpus": true
      },
      "thermo.energy_above_hull": {
        "title_zh": "凸包上能量",
        "source_field": "thermo.energy_above_hull",
        "unit": "eV/atom",
        "method": "QMOF-Thermo PBE-D3(BJ), published reference phases",
        "geometry_method": "PBE-D3BJ",
        "require_method_in_question_or_answer": false,
        "method_in_metadata": true,
        "enabled_for_corpus": true
      }
    },
    "rendered_values": {
      "formula": "LiBC4F2H3NO4",
      "atom_count": "64",
      "crystal_system": "orthorhombic",
      "formation_energy": "-1.182326",
      "energy_above_hull": "0.191693"
    },
    "geometry_method": "PBE-D3BJ",
    "source_name": "MALKES_FSR",
    "present_in_llm4mat": false,
    "holdout_from_training": false,
    "llm4mat_name_matches": [],
    "sampling_seed": 20260910,
    "description_group": "thermodynamics",
    "description_modules": [
      "thermodynamics"
    ]
  }
}
```
