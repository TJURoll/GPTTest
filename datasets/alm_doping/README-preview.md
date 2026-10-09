# alm_doping 格式预览

这是解压后的数据格式预览，**不是完整数据集**。

1 MiB 以内的普通文本、数据、说明和 schema 文件保留原始完整内容；更大的主语料 messages/*.jsonl 最多保留前 500 条完整且可解析的源记录，辅助 JSONL 最多保留前 5 条。较大 CSV/TSV 保存表头和前 5 个物理数据行，TXT 保存前 5 行。每行上限 1 MiB、每个预览文件上限 10 MiB；超限时保留此前完整记录并写明原因，不保存残缺 JSON。

结构资源最多 100 个，优先选择样例消息引用的文件，另外保留少量顺序样例。优先引用来自各主语料文件的前 5 条记录；扩大的主语料样例中的其他结构引用可能未包含，清单会逐项列出。Parquet 只保存 footer 行数和字段结构，不包含二进制表体或数据行。脚本文件仅作为数据保存，未执行。

完整来源数量、实际导出数量、选择方法、未包含资源汇总及缺少的结构引用见 [preview-manifest.json](preview-manifest.json)。

`others/` 中保留的原始说明、清单、报告和哈希描述完整来源包或历史导出；它们不是这个 GitHub 子集的数量或校验值。当前子集以 `preview-manifest.json` 为准，截取后的文件不能使用完整来源文件的哈希校验。

## 直接查看样例

按掺杂约束编辑晶体结构，含输入和输出 CIF。

| 主对话文件 | 完整来源物理行数 | 本仓库记录数 | 保存方式 |
| --- | ---: | ---: | --- |
| [messages/train.jsonl](messages/train.jsonl) | 6,403 | 500 | first500 |
| [messages/val.jsonl](messages/val.jsonl) | 525 | 500 | first500 |

结构资产：完整来源 9,098 个，本仓库保留 40 个。

原始格式说明：[others/README_layout_zh.md](others/README_layout_zh.md)；[others/README_zh.md](others/README_zh.md)。

原包提供的辅助预览：[others/preview.jsonl](others/preview.jsonl)；[others/preview.md](others/preview.md)（数量单独统计）。

结构格式样例：[structures/ff/ff00dfb90c49d8763fa708043d4e2b2d1cea82afe79d1abee48c9d92511062aa.cif](structures/ff/ff00dfb90c49d8763fa708043d4e2b2d1cea82afe79d1abee48c9d92511062aa.cif)。

### 一条真实记录

以下只调整缩进；字段和值来自上面第一个主对话文件的第一条记录。

```json
{
  "id": "alm.doping_bounded.736216",
  "input_cif_path": "structures/01/01c6f53530ef78be3a86c6ca38e02da3e4a9ae8812a87e8fa812f81feb738611.cif",
  "input_cif_relative_path": "structures/01/01c6f53530ef78be3a86c6ca38e02da3e4a9ae8812a87e8fa812f81feb738611.cif",
  "input_cif_sha256": "72c38ff967ab0c97e2a9d46d83bf5839b3a8fd04ddaba551fce6d90546a1b881",
  "input_geometry_sha256": "01c6f53530ef78be3a86c6ca38e02da3e4a9ae8812a87e8fa812f81feb738611",
  "messages": [
    {
      "content": "Substitute Gd for all Tb atoms while keeping the overall atomic arrangement close to the original. Leave the other elements unchanged and allow only small lattice and local positional changes.",
      "role": "user"
    },
    {
      "content": "This structure fulfills the complete Tb to Gd substitution while retaining a near-original atomic arrangement.",
      "role": "assistant"
    }
  ],
  "metadata": {
    "constraints": {
      "donor": "Tb",
      "dopant": "Gd"
    },
    "dataset": "ALM",
    "geometry_evidence": {
      "allowed_principal_stretch_range": [
        0.95,
        1.05
      ],
      "max_allowed_displacement_A": 0.1,
      "maximum_displacement_A": 0.01704891148849546,
      "principal_stretches": [
        1.0055980320848383,
        1.0055980320848381,
        1.0055980320848381
      ]
    },
    "geometry_evidence_file": "/mnt/e/Datasets/Inorganic_Materials/ALM_dataset/doping_bounded_checked/geometry_candidates.jsonl",
    "parent": "mp_3d_2020",
    "provenance": {
      "input": {
        "current_deprecation_checked": false,
        "endpoint_id": "a6a900ee1604ba18e513dc9c1f4392d28bcaa91e44bb6e973a7ffb731f41b118",
        "matched_reference_ids": [
          "77af325e400a94e371bd5f2bb482e62fea3114449b88eb083734b6ff75b2d950"
        ],
        "native_id": "mp-14387",
        "source_status": "verified_geometry_no_known_source_warning"
      },
      "output": {
        "current_deprecation_checked": false,
        "endpoint_id": "271fcd01d15583bbf30ac68cf960582c6742af5ed7f727b7fed60591dc0833b7",
        "matched_reference_ids": [
          "47de8b689713317178641368867b6648e554cbd90acfcf3c6955a92668258865"
        ],
        "native_id": "mp-14133",
        "source_status": "verified_geometry_no_known_source_warning"
      }
    },
    "query_template_id": "query_03",
    "response_template_id": "response_05",
    "sampling_seed": 20260912,
    "selection_file": "/mnt/e/Datasets/Inorganic_Materials/ALM_dataset/doping_bounded_checked/usable_unique_pairs.jsonl",
    "source_evidence_file": "/mnt/e/Datasets/Inorganic_Materials/ALM_dataset/doping_bounded_checked/endpoint_source_checks.jsonl",
    "source_file": "/mnt/e/Datasets/Inorganic_Materials/ALM_dataset/alm_bench/doping.parquet",
    "source_row_id": "doping_strain-mp-mp-14387-to-mp-14133-Tb_to_Gd-dV_+1.69pct-sg_1-n_uniq_3",
    "source_row_index": 736216,
    "split_origin": "unassigned_new_component",
    "template_group": "bounded_all_site_substitution"
  },
  "output_cif_path": "structures/7f/7f0757bd1545162ba2dd0598f5290d999bd8630a22c77dc78255070c1aacc3f1.cif",
  "output_cif_relative_path": "structures/7f/7f0757bd1545162ba2dd0598f5290d999bd8630a22c77dc78255070c1aacc3f1.cif",
  "output_cif_sha256": "8640d30f676cff1d45ded11e935f3ce17b20bfd60ae5e2911c10e330dc07acd3",
  "output_geometry_sha256": "7f0757bd1545162ba2dd0598f5290d999bd8630a22c77dc78255070c1aacc3f1",
  "split": "train",
  "split_group_id": "0143542f579605e587ca4c13cfa933ece104668356ee90da95c61d2829ba654e",
  "task": "doping"
}
```
