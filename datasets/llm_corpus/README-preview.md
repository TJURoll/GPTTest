# llm_corpus 格式预览

这是解压后的数据格式预览，**不是完整数据集**。

1 MiB 以内的普通文本、数据、说明和 schema 文件保留原始完整内容；更大的主语料 messages/*.jsonl 最多保留前 500 条完整且可解析的源记录，辅助 JSONL 最多保留前 5 条。较大 CSV/TSV 保存表头和前 5 个物理数据行，TXT 保存前 5 行。每行上限 1 MiB、每个预览文件上限 10 MiB；超限时保留此前完整记录并写明原因，不保存残缺 JSON。

结构资源最多 100 个，优先选择样例消息引用的文件，另外保留少量顺序样例。优先引用来自各主语料文件的前 5 条记录；扩大的主语料样例中的其他结构引用可能未包含，清单会逐项列出。Parquet 只保存 footer 行数和字段结构，不包含二进制表体或数据行。脚本文件仅作为数据保存，未执行。

完整来源数量、实际导出数量、选择方法、未包含资源汇总及缺少的结构引用见 [preview-manifest.json](preview-manifest.json)。

`others/` 中保留的原始说明、清单、报告和哈希描述完整来源包或历史导出；它们不是这个 GitHub 子集的数量或校验值。当前子集以 `preview-manifest.json` 为准，截取后的文件不能使用完整来源文件的哈希校验。

## 直接查看样例

FG26 光谱或三维分子结构到性质、SELFIES 和官能团等回答。

| 主对话文件 | 完整来源物理行数 | 本仓库记录数 | 保存方式 |
| --- | ---: | ---: | --- |
| [messages/train.jsonl](messages/train.jsonl) | 1,355,530 | 500 | first500 |
| [messages/val.jsonl](messages/val.jsonl) | 71,552 | 500 | first500 |

结构资产：完整来源 233,948 个，本仓库保留 25 个。

原始格式说明：[others/README_zh.md](others/README_zh.md)；[others/README_layout_zh.md](others/README_layout_zh.md)。

原包提供的辅助预览：[others/preview.md](others/preview.md)；[others/preview.jsonl](others/preview.jsonl)（数量单独统计）。

结构格式样例：[structures/93/9347c1bd4e24ab5bc07a77a35d3526eb23ac7fcb818ba0b61f195d6bffcb827f.xyz](structures/93/9347c1bd4e24ab5bc07a77a35d3526eb23ac7fcb818ba0b61f195d6bffcb827f.xyz)。

光谱字段和行数样例：[spectra/train_fg26_broad-nmr-h_spectra.parquet.metadata.json](spectra/train_fg26_broad-nmr-h_spectra.parquet.metadata.json)（元数据，不含数值行）。

### 一条真实记录

以下只调整缩进；字段和值来自上面第一个主对话文件的第一条记录。

```json
{
  "sample_id": "fg26_31052_spectra_selfies_nonisomeric_0",
  "record_index": 31052,
  "key_id": "518aabaf794877d450c66db69a00e27da4e247f6947162f0ecd346e4e05e7f8e",
  "split": "train",
  "task": "selfies_nonisomeric",
  "input_mode": "spectra",
  "variant": 0,
  "query_template_id": "selfies_nonisomeric.q12",
  "input_preamble_template_id": "multiple_spectra.p17",
  "target_fields": [
    "canonical_selfies"
  ],
  "response_template_id": "selfies_nonisomeric.responses.r01",
  "messages": [
    {
      "role": "user",
      "content": "Your inputs are the infrared and broadened hydrogen NMR spectra of the same molecule. Write this molecule's connectivity as SELFIES."
    },
    {
      "role": "assistant",
      "content": "[C][C][O][C][Ring1][Ring1][C][=Branch1][C][=O][N][C][C][=Branch1][C][=O][N][Branch1][C][C][O]"
    }
  ],
  "spectrum_types": [
    "ir",
    "broad-nmr-h"
  ],
  "input_spectrum_refs": [
    {
      "spectrum_type": "ir",
      "source_path": "spectra/train_fg26_ir_spectra.parquet",
      "row_group": 597,
      "row_in_group": 32,
      "row_index": 152864,
      "dtype": "<f8",
      "shape": [
        4000
      ],
      "data_sha256": "f34aaffc8d3408d3d5cb7cd6de152941f5247e2ca576544170c6fb55c4187d7c",
      "key_id": "518aabaf794877d450c66db69a00e27da4e247f6947162f0ecd346e4e05e7f8e",
      "axis_metadata_id": "ir"
    },
    {
      "spectrum_type": "broad-nmr-h",
      "source_path": "spectra/train_fg26_broad-nmr-h_spectra.parquet",
      "row_group": 597,
      "row_in_group": 32,
      "row_index": 152864,
      "dtype": "<f8",
      "shape": [
        4000
      ],
      "data_sha256": "82f7db7d26c9823641c368f65addd7c4e73a0a97947f7498dcd68f59a2f09968",
      "key_id": "518aabaf794877d450c66db69a00e27da4e247f6947162f0ecd346e4e05e7f8e",
      "axis_metadata_id": "broad-nmr-h"
    }
  ],
  "selfies_policy": "rdkit_canonical_nonisomeric_muse_style"
}
```
