# MOF LLM Corpus

`data.jsonl` 每行是一条单结构问答。仅使用最终筛选结果，不收录原始抽取、历史测试、备份、已隔离问答或模型思考内容。

## 文件布局

```text
llm_corpus/
  data.jsonl
  cifs/<paper_id>/<ccdc_refcode>.cif
  provenance.jsonl
  summary.json
  README.md
```

每条训练样本只有三个字段：

```json
{"qa_id":"<paper_id>:<cif_stem>:<original_qa_number>","cif_path":"cifs/<paper_id>/<cif_stem>.cif","messages":[{"role":"user","content":"<question>"},{"role":"assistant","content":"<answer>"}]}
```

`cif_path` 相对于本目录。同一结构的多条 QA 引用同一个 CIF 文件，不重复存储坐标；不同论文的同名文件不会相互覆盖。CIF 是源文件的逐字节副本，不是摘要或重新导出的结构。`messages` 只包含原有的最终 Q/A，没有 system 消息、文章、证据或结构占位符。结构编码器应读取对应的 CIF 文件，不能把路径字符串本身当成结构输入。

`provenance.jsonl` 单独保存逐结构的来源、原始路径、哈希和 QA 数量。零 QA 的结构仅在这个来源清单中留记录，没有训练样本，也不复制无用的 CIF。该文件不是训练对话。

`summary.json` 包含实际条数、结构数、来源统计和完整性校验结果。来源指原生产流程，后续人工修订另有审计记录，并不冒充原模型输出。

## Jupyter 读取

```python
from pathlib import Path
import json

ROOT = Path(r"E:\Datasets\MOF_papers\llm_corpus")
with (ROOT / "data.jsonl").open(encoding="utf-8") as f:
    sample = json.loads(next(f))

question = sample["messages"][0]["content"]
answer = sample["messages"][1]["content"]
cif_path = ROOT / sample["cif_path"]
cif_text = cif_path.read_text(encoding="utf-8")

print(sample["qa_id"])
print(question)
print(answer)
print(cif_path)
```

本次没有进行训练/验证/测试划分。后续划分至少按论文分组，并根据具体评测目标考虑相同结构、材料家族的跨论文泄漏。没有因为可疑关键词或低信息量而额外批量删改 QA；这是一份最终结果的忠实导出，不是对全库科学正确性的认证。
