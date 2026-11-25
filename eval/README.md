# eval —— 阶段二的 AI 评测层

评的是「AI 会不会讲题」，不是「题库查得准不准」。所以这里另开一套：阶段一的 `service/` 一行不动，它那套 `contains` 匹配评的是数据、不评 AI。

## 目录结构

```
eval/
├── agent.py              被测对象：把模型包成「初中数学答疑老师」
├── llm_client.py         唯一的 HTTP 出口，只负责发请求、取回文本
├── cases/
│   └── knowledge.json    用例：题面（可多轮）+ 期望答案
├── judges/
│   └── knowledge.py      维度 1 判分器：题目 + 标准答案 + 作答 → 三档判定
├── run_eval.py           串联：读用例 → 答题 → 判分 → 落盘
└── results.json          运行产物，每次覆盖，已进 .gitignore
```

四层各管一件事，谁也不知道别人从哪拿的数据：`llm_client` 不知道自己在评什么，`agent` 不知道题从哪来，`judge` 不知道成绩怎么汇总，`run_eval` 只串流程。要换模型、换用例、换判分标准，各改各的。

## 两个模型、两家厂商

| 角色 | 模型 | 温度 | 环境变量 | 接口 |
|---|---|---|---|---|
| 被测（答题） | `deepseek-chat` | 0.3 | `LLM_API_KEY` | `api.deepseek.com` |
| 判分（Judge） | `glm-4-flash` | 0 | `JUDGE_API_KEY` | `open.bigmodel.cn` |

分家的理由就一条：避开自我偏好偏差（self-preference）——不能让自己的同类判自己，否则它给高分往往是因为「风格像我」，不是因为答案对。

两个 key 都从环境变量读，不写进代码、不进仓库。

## 怎么跑

在**仓库根目录**用 `-m` 跑，不要 `cd` 进 `eval/`：

```bash
python -m eval.run_eval             # 跑全部用例，出成绩
python -m eval.agent                # 只测被测模型，看它怎么答一道题
python -m eval.judges.knowledge     # 只测判分器，喂一条已知算错的答卷
```

必须 `-m` 的原因：包内用的是 `from eval.agent import answer` 这类按包名的绝对导入。直接 `python eval/run_eval.py` 启动时，`eval` 不在搜索路径里，会报找不到模块。

## 输出：results.json

一条用例一个对象，五个字段：

| 字段 | 含义 |
|---|---|
| `id` | 用例编号，如 `g7-eq-001` |
| `answer` | 被测模型的作答原文（最后一轮） |
| `verdict` | `pass` / `partial` / `fail` |
| `error_type` | `method_error` / `final_answer_error` / `knowledge_error` / `null` |
| `reason` | 判分器给的一句话理由 |

存 `answer` 是为了事后回查：判分器说「得数正确」，得能翻出原文看它到底算对没有。只存结论的话，判错了也查不出来。

末尾还会打印一句 `N条用例，M条通过`，方便肉眼扫一眼。

## 三档怎么分（维度 1：知识点正确性）

- **`pass`**：得数正确，引用的定理、公式名称也对。
- **`partial`**：得数对但定理用错（属于蒙对）；或者方法对、中间步骤对，只是最后一步得数抄错。
- **`fail`**：得数错且过程也错，或引用了根本不存在的定理。

这个档位只判「知识点正确性」一件事。步骤跳不跳、讲没超纲、讲深讲浅、话说得长不长，都不在这一维扣分——那是维度 2、3、4 的事。

## 已知问题（都还没修）

1. **只判最后一轮**。多轮用例（如 `g7-eq-002`）只取 `turns[-1]` 与 `replies[-1]`，前一轮讲错了不会被发现。
2. **`reason` 不可信**。连跑三次的实测：档位 12 次全一致，但理由每次都换措辞，还出现过两道不同的题给出同一句理由、并把「定理、公式名称也对」安在一道没引任何定理的应用题上。详见 `docs/ai-eval-notes.md` 第六、七节。
3. **只有 4 条用例、只落地了维度 1**。六个维度的判法、失败样例和覆盖计划在 `docs/eval-dimensions.md`，另外五个还停在纸面。

第 2 条是当前最值得改的：一条 `pass` 现在只说明判分器没发现问题，不说明它真检查过。

## 相关文档

- `docs/eval-dimensions.md` —— 六个维度：判什么、用什么判、判定标准、失败样例、覆盖计划
- `docs/ai-eval-notes.md` —— LLM-as-Judge 原理、三个已知偏差、判分器自检与稳定性观察
- `docs/curriculum-reference.md` —— 超纲检测的教材章节，允许清单与黑名单
