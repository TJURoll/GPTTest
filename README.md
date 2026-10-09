# 化学与材料数据格式预览

本仓库保存 **11 个数据集的解压格式样例，是不完整子集**，用于查看字段、对话、结构文件和光谱存储格式。

**完整来源主对话 JSONL 共 4,857,910 个物理行；仓库保留其中 11,500 条记录（23 个文件各前 500 条）。** 辅助预览、索引和清单单独统计，不算作新增主对话。16 个光谱 Parquet 共 1,910,952 行，单独计数。

完整来源还包含 528,947 个 CIF 和 233,948 个 XYZ；本仓库仅保留少量完整结构文件。

点击数据集名称可看到一条排版后的真实记录；`messages/*.jsonl` 是可解析的源数据截取，`structures/` 保存少量完整 CIF/XYZ，`others/` 保存原始格式说明及小文件。

部分数据集的 `others/preview*` 还包含原包提供的任务示例，可结合主对话截取查看不同任务的字段。

| 数据集 | 内容 | 完整 train 行数 | 完整 val 行数 | 其他主对话划分 | 原始结构数 → 保留数 |
| --- | --- | ---: | ---: | --- | ---: |
| [alm_csp_atomtxt](datasets/alm_csp_atomtxt/README-preview.md) | 化学式、晶系和空间群约束下的晶体结构生成 | 105,698 | 11,705 | — | 112,485 → 30 |
| [alm_doping](datasets/alm_doping/README-preview.md) | 按掺杂约束编辑晶体结构，含输入和输出 CIF | 6,403 | 525 | — | 9,098 → 40 |
| [alm_polymorph](datasets/alm_polymorph/README-preview.md) | 相同组分的多晶型结构转换，含结构对和能量信息 | 13,677 | 669 | — | 10,922 → 40 |
| [atomworldbench](datasets/atomworldbench/README-preview.md) | 晶体原子编辑任务，另含 bench 评测划分 | 57,452 | — | bench: 9,424 | 133,752 → 40 |
| [chebi20](datasets/chebi20/README-preview.md) | SMILES 到英文分子描述 | 26,407 | 3,301 | test: 3,300 | 0 → 0 |
| [hmof](datasets/hmof/README-preview.md) | MOF 吸附、孔径、空隙率和表面积等性质问答 | 534,879 | 28,153 | — | 70,634 → 30 |
| [llm_corpus](datasets/llm_corpus/README-preview.md) | FG26 光谱或三维分子结构到性质、SELFIES 和官能团等回答 | 1,355,530 | 71,552 | — | 233,948 → 25 |
| [matterchat](datasets/matterchat/README-preview.md) | 材料性质问答，另含 gnome 外部评测划分 | 1,478,871 | 164,209 | gnome: 177,922 | 158,382 → 35 |
| [mof_papers](datasets/mof_papers/README-preview.md) | 论文来源的 MOF 结构与性质问答，未预设 train/val | — | — | 未划分: 101,991 | 13,302 → 21 |
| [molopt](datasets/molopt/README-preview.md) | 按 QED、HBD、HBA 等约束编辑 SMILES | 340,294 | 19,624 | — | 0 → 0 |
| [qmof](datasets/qmof/README-preview.md) | QMOF 材料性质问答 | 311,695 | 34,629 | — | 20,372 → 30 |

## 保留规则与数量含义

- 普通文本、数据、说明和 schema 文件不超过 1 MiB 时，保留原始完整内容。
- 大主对话 JSONL 保留前 500 条完整记录，大辅助 JSONL 保留前 5 条；大 CSV/TSV 保留表头及前 5 个物理数据行，TXT 保留前 5 行。其他大 JSON 只保留字段预览元数据。
- 大量 CIF/XYZ 资产最多每包 100 个，优先保留早期样例消息引用的结构，再加少量顺序样例。所选结构文件本身完整；其余消息中的结构路径可能指向未包含资产，缺失数量在各包清单中注明。
- 大 Parquet 仅保存 `.parquet.metadata.json`，包含精确 footer 行数和字段结构；没有上传二进制表体或数值数据行。
- 这些是顺序格式样例，不代表类别比例、随机抽样或完整训练/评测数据。

`others/` 中保留的原始说明、清单、报告和哈希描述完整来源包或历史导出；它们不是这个 GitHub 子集的数量或校验值。当前子集以 `preview-manifest.json` 为准，截取后的文件不能使用完整来源文件的哈希校验。

原始主对话、辅助 JSONL 和 Parquet 的逐文件数量见 [ORIGINAL-COUNTS.md](ORIGINAL-COUNTS.md)，机器可读版本见 [counts.json](counts.json)。JSONL 行数是完整解压流的物理行计数，不表示唯一分子数，也不表示全量 JSON 语义校验。所有保留的 JSONL 记录均已实际解析。

本仓库预览文件的大小和 SHA-256 见 [preview-checksums.json](preview-checksums.json)。

`llm_corpus` 是独立的 FG26 语料。光谱 Parquet 原始文件名中的 train/test 与对话 train/val 含义不同；对话划分以 `messages/` 为准。光谱字段为 `key`、`dtype`、`shape`、`data`，对话记录通过文件、行组和组内行号引用光谱。

## 读取样例

在仓库根目录运行，只读取保留的 JSONL：

```python
import json
from pathlib import Path

path = Path("datasets/chebi20/messages/train.jsonl")
with path.open(encoding="utf-8") as f:
    record = json.loads(next(f))
print(record["messages"])
```

样例保留原始字段和值；不同数据集的 `metadata`、任务标签和结构引用字段各有不同，详见每包的真实记录和原始说明。
