# 完整来源逐文件数量

以下为完整来源文件的精确计数；本仓库中的文件按预览规则保存。JSONL 采用物理行数，Parquet 采用 footer 行数，两者分别统计。

主对话：4,857,910 行；辅助 JSONL：2,653,733 行。

| 数据集 | 文件 | 类型 | 原始行数 | 保留记录数 | 保存方式 |
| --- | --- | --- | ---: | ---: | --- |
| alm_csp_atomtxt | [messages/train.jsonl](datasets/alm_csp_atomtxt/messages/train.jsonl) | 主对话 | 105,698 | 500 | first500 |
| alm_csp_atomtxt | [messages/val.jsonl](datasets/alm_csp_atomtxt/messages/val.jsonl) | 主对话 | 11,705 | 500 | first500 |
| alm_csp_atomtxt | [others/asset_manifest.jsonl](datasets/alm_csp_atomtxt/others/asset_manifest.jsonl) | 辅助 | 112,485 | 5 | first5 |
| alm_csp_atomtxt | [others/preview.jsonl](datasets/alm_csp_atomtxt/others/preview.jsonl) | 辅助 | 10 | 10 | FULL |
| alm_csp_atomtxt | [others/split_manifest.jsonl](datasets/alm_csp_atomtxt/others/split_manifest.jsonl) | 辅助 | 107,449 | 5 | first5 |
| alm_csp_atomtxt | [others/structure_index.jsonl](datasets/alm_csp_atomtxt/others/structure_index.jsonl) | 辅助 | 112,485 | 5 | first5 |
| alm_doping | [messages/train.jsonl](datasets/alm_doping/messages/train.jsonl) | 主对话 | 6,403 | 500 | first500 |
| alm_doping | [messages/val.jsonl](datasets/alm_doping/messages/val.jsonl) | 主对话 | 525 | 500 | first500 |
| alm_doping | [others/asset_manifest.jsonl](datasets/alm_doping/others/asset_manifest.jsonl) | 辅助 | 9,098 | 5 | first5 |
| alm_doping | [others/preview.jsonl](datasets/alm_doping/others/preview.jsonl) | 辅助 | 5 | 5 | FULL |
| alm_doping | [others/split_manifest.jsonl](datasets/alm_doping/others/split_manifest.jsonl) | 辅助 | 3,102 | 3,102 | FULL |
| alm_doping | [others/structure_index.jsonl](datasets/alm_doping/others/structure_index.jsonl) | 辅助 | 9,098 | 5 | first5 |
| alm_polymorph | [messages/train.jsonl](datasets/alm_polymorph/messages/train.jsonl) | 主对话 | 13,677 | 500 | first500 |
| alm_polymorph | [messages/val.jsonl](datasets/alm_polymorph/messages/val.jsonl) | 主对话 | 669 | 500 | first500 |
| alm_polymorph | [others/asset_manifest.jsonl](datasets/alm_polymorph/others/asset_manifest.jsonl) | 辅助 | 10,922 | 5 | first5 |
| alm_polymorph | [others/pair_selection.jsonl](datasets/alm_polymorph/others/pair_selection.jsonl) | 辅助 | 200,899 | 5 | first5 |
| alm_polymorph | [others/preview.jsonl](datasets/alm_polymorph/others/preview.jsonl) | 辅助 | 6 | 6 | FULL |
| alm_polymorph | [others/split_geometry_checks.jsonl](datasets/alm_polymorph/others/split_geometry_checks.jsonl) | 辅助 | 112,753 | 5 | first5 |
| alm_polymorph | [others/split_manifest.jsonl](datasets/alm_polymorph/others/split_manifest.jsonl) | 辅助 | 3,298 | 3,298 | FULL |
| alm_polymorph | [others/split_nodes.jsonl](datasets/alm_polymorph/others/split_nodes.jsonl) | 辅助 | 143,427 | 5 | first5 |
| alm_polymorph | [others/structure_index.jsonl](datasets/alm_polymorph/others/structure_index.jsonl) | 辅助 | 10,922 | 5 | first5 |
| alm_polymorph | [others/structure_roundtrip_checks.jsonl](datasets/alm_polymorph/others/structure_roundtrip_checks.jsonl) | 辅助 | 10,922 | 5 | first5 |
| alm_polymorph | [others/excluded_from_corpus/split_holds.jsonl](datasets/alm_polymorph/others/excluded_from_corpus/split_holds.jsonl) | 辅助 | 186,553 | 5 | first5 |
| atomworldbench | [messages/bench.jsonl](datasets/atomworldbench/messages/bench.jsonl) | 主对话 | 9,424 | 500 | first500 |
| atomworldbench | [messages/train.jsonl](datasets/atomworldbench/messages/train.jsonl) | 主对话 | 57,452 | 500 | first500 |
| atomworldbench | [others/asset_manifest.jsonl](datasets/atomworldbench/others/asset_manifest.jsonl) | 辅助 | 133,752 | 5 | first5 |
| atomworldbench | [others/preview.jsonl](datasets/atomworldbench/others/preview.jsonl) | 辅助 | 105 | 105 | FULL |
| chebi20 | [messages/test.jsonl](datasets/chebi20/messages/test.jsonl) | 主对话 | 3,300 | 500 | first500 |
| chebi20 | [messages/train.jsonl](datasets/chebi20/messages/train.jsonl) | 主对话 | 26,407 | 500 | first500 |
| chebi20 | [messages/validation.jsonl](datasets/chebi20/messages/validation.jsonl) | 主对话 | 3,301 | 500 | first500 |
| chebi20 | [others/asset_manifest.jsonl](datasets/chebi20/others/asset_manifest.jsonl) | 辅助 | 0 | 0 | FULL |
| hmof | [messages/train.jsonl](datasets/hmof/messages/train.jsonl) | 主对话 | 534,879 | 500 | first500 |
| hmof | [messages/val.jsonl](datasets/hmof/messages/val.jsonl) | 主对话 | 28,153 | 500 | first500 |
| hmof | [others/asset_manifest.jsonl](datasets/hmof/others/asset_manifest.jsonl) | 辅助 | 70,634 | 5 | first5 |
| hmof | [others/preview.jsonl](datasets/hmof/others/preview.jsonl) | 辅助 | 24 | 24 | FULL |
| hmof | [others/structure_index.jsonl](datasets/hmof/others/structure_index.jsonl) | 辅助 | 70,634 | 5 | first5 |
| llm_corpus | [others/asset_manifest.jsonl](datasets/llm_corpus/others/asset_manifest.jsonl) | 辅助 | 233,964 | 5 | first5 |
| llm_corpus | [others/spectrum_index.jsonl](datasets/llm_corpus/others/spectrum_index.jsonl) | 辅助 | 233,948 | 5 | first5 |
| llm_corpus | [others/preview.jsonl](datasets/llm_corpus/others/preview.jsonl) | 辅助 | 140 | 140 | FULL |
| llm_corpus | [others/structure_index.jsonl](datasets/llm_corpus/others/structure_index.jsonl) | 辅助 | 233,948 | 5 | first5 |
| llm_corpus | [messages/train.jsonl](datasets/llm_corpus/messages/train.jsonl) | 主对话 | 1,355,530 | 500 | first500 |
| llm_corpus | [messages/val.jsonl](datasets/llm_corpus/messages/val.jsonl) | 主对话 | 71,552 | 500 | first500 |
| matterchat | [messages/gnome.jsonl](datasets/matterchat/messages/gnome.jsonl) | 主对话 | 177,922 | 500 | first500 |
| matterchat | [messages/train.jsonl](datasets/matterchat/messages/train.jsonl) | 主对话 | 1,478,871 | 500 | first500 |
| matterchat | [messages/val.jsonl](datasets/matterchat/messages/val.jsonl) | 主对话 | 164,209 | 500 | first500 |
| matterchat | [others/asset_manifest.jsonl](datasets/matterchat/others/asset_manifest.jsonl) | 辅助 | 158,382 | 5 | first5 |
| matterchat | [others/preview.jsonl](datasets/matterchat/others/preview.jsonl) | 辅助 | 144 | 144 | FULL |
| matterchat | [others/skipped_tasks.jsonl](datasets/matterchat/others/skipped_tasks.jsonl) | 辅助 | 79,582 | 5 | first5 |
| matterchat | [others/structures.jsonl](datasets/matterchat/others/structures.jsonl) | 辅助 | 158,382 | 5 | first5 |
| matterchat | [others/structure_file_index.jsonl](datasets/matterchat/others/structure_file_index.jsonl) | 辅助 | 158,382 | 5 | first5 |
| mof_papers | [messages/data.jsonl](datasets/mof_papers/messages/data.jsonl) | 主对话 | 101,991 | 500 | first500 |
| mof_papers | [others/asset_manifest.jsonl](datasets/mof_papers/others/asset_manifest.jsonl) | 辅助 | 13,302 | 5 | first5 |
| mof_papers | [others/provenance.jsonl](datasets/mof_papers/others/provenance.jsonl) | 辅助 | 13,801 | 5 | first5 |
| molopt | [messages/train.jsonl](datasets/molopt/messages/train.jsonl) | 主对话 | 340,294 | 500 | first500 |
| molopt | [messages/val.jsonl](datasets/molopt/messages/val.jsonl) | 主对话 | 19,624 | 500 | first500 |
| molopt | [others/asset_manifest.jsonl](datasets/molopt/others/asset_manifest.jsonl) | 辅助 | 0 | 0 | FULL |
| molopt | [others/preview.jsonl](datasets/molopt/others/preview.jsonl) | 辅助 | 12 | 12 | FULL |
| qmof | [messages/train.jsonl](datasets/qmof/messages/train.jsonl) | 主对话 | 311,695 | 500 | first500 |
| qmof | [messages/val.jsonl](datasets/qmof/messages/val.jsonl) | 主对话 | 34,629 | 500 | first500 |
| qmof | [others/asset_manifest.jsonl](datasets/qmof/others/asset_manifest.jsonl) | 辅助 | 20,372 | 5 | first5 |
| qmof | [others/preview.jsonl](datasets/qmof/others/preview.jsonl) | 辅助 | 47 | 47 | FULL |
| qmof | [others/split_manifest.jsonl](datasets/qmof/others/split_manifest.jsonl) | 辅助 | 20,372 | 5 | first5 |
| qmof | [others/structure_index.jsonl](datasets/qmof/others/structure_index.jsonl) | 辅助 | 20,372 | 5 | first5 |

## 光谱 Parquet

以下表体未上传。链接文件仅展示 footer schema 与数量；footer 行数和行组数量一致，但未解码和校验数据页。

| 文件 | 完整来源行数 | 上传数值行数 |
| --- | ---: | ---: |
| [spectra/train_fg26_broad-nmr-h_spectra.parquet](datasets/llm_corpus/spectra/train_fg26_broad-nmr-h_spectra.parquet.metadata.json) | 214,982 | 0 |
| [spectra/test_fg26_broad-nmr-h_spectra.parquet](datasets/llm_corpus/spectra/test_fg26_broad-nmr-h_spectra.parquet.metadata.json) | 23,887 | 0 |
| [spectra/train_fg26_ir_spectra.parquet](datasets/llm_corpus/spectra/train_fg26_ir_spectra.parquet.metadata.json) | 214,982 | 0 |
| [spectra/test_fg26_xas-n_spectra.parquet](datasets/llm_corpus/spectra/test_fg26_xas-n_spectra.parquet.metadata.json) | 23,887 | 0 |
| [spectra/train_fg26_broad-nmr-c_spectra.parquet](datasets/llm_corpus/spectra/train_fg26_broad-nmr-c_spectra.parquet.metadata.json) | 214,982 | 0 |
| [spectra/test_fg26_raman_spectra.parquet](datasets/llm_corpus/spectra/test_fg26_raman_spectra.parquet.metadata.json) | 23,887 | 0 |
| [spectra/train_fg26_xas-n_spectra.parquet](datasets/llm_corpus/spectra/train_fg26_xas-n_spectra.parquet.metadata.json) | 214,982 | 0 |
| [spectra/test_fg26_xas-o_spectra.parquet](datasets/llm_corpus/spectra/test_fg26_xas-o_spectra.parquet.metadata.json) | 23,887 | 0 |
| [spectra/train_fg26_xas-c_spectra.parquet](datasets/llm_corpus/spectra/train_fg26_xas-c_spectra.parquet.metadata.json) | 214,982 | 0 |
| [spectra/test_fg26_xas-c_spectra.parquet](datasets/llm_corpus/spectra/test_fg26_xas-c_spectra.parquet.metadata.json) | 23,887 | 0 |
| [spectra/test_fg26_ir_spectra.parquet](datasets/llm_corpus/spectra/test_fg26_ir_spectra.parquet.metadata.json) | 23,887 | 0 |
| [spectra/train_fg26_uv_spectra.parquet](datasets/llm_corpus/spectra/train_fg26_uv_spectra.parquet.metadata.json) | 214,982 | 0 |
| [spectra/test_fg26_uv_spectra.parquet](datasets/llm_corpus/spectra/test_fg26_uv_spectra.parquet.metadata.json) | 23,887 | 0 |
| [spectra/test_fg26_broad-nmr-c_spectra.parquet](datasets/llm_corpus/spectra/test_fg26_broad-nmr-c_spectra.parquet.metadata.json) | 23,887 | 0 |
| [spectra/train_fg26_raman_spectra.parquet](datasets/llm_corpus/spectra/train_fg26_raman_spectra.parquet.metadata.json) | 214,982 | 0 |
| [spectra/train_fg26_xas-o_spectra.parquet](datasets/llm_corpus/spectra/train_fg26_xas-o_spectra.parquet.metadata.json) | 214,982 | 0 |

Parquet 合计：1,910,952 行。
