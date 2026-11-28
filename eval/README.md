# eval —— 阶段二的 AI 评测层

评的是「AI 会不会讲题」，不是「题库查得准不准」。所以这里另开一套：阶段一的 `service/` 一行不动，它那套 `contains` 匹配评的是数据、不评 AI。

## 目录结构

```
eval/
├── agent.py              被测对象：把模型包成「初中数学答疑老师」
├── llm_client.py         唯一的 HTTP 出口，只负责发请求、取回文本
├── cases/                六个用例文件，一维一份，共 19 条
│   ├── knowledge.json            （4 条）
│   ├── step_consistency.json     （4 条）
│   ├── out_of_scope.json         （3 条）
│   ├── level_matching.json       （2 条）
│   ├── multi_turn_stability.json （2 条）
│   └── hallucination.json        （4 条）
├── judges/               六个判分器，一维一份
│   ├── knowledge.py          维度 1 知识点正确性（题目 + 标准答案 + 作答）
│   ├── step_consistency.py   维度 2 步骤一致性（不喂标准答案）
│   ├── out_of_scope.py       维度 3 超纲检测（含规则层扫描）
│   ├── level_matching.py     维度 4 分层讲解匹配（按 grade 分档）
│   ├── multi_turn.py         维度 5 多轮稳定性（拿整串对话）
│   └── hallucination.py      维度 6 幻觉率（不喂标准答案，判引用真伪）
├── run_eval.py           串联：读用例 → 答题 → 判分 → 落盘
└── results.json          运行产物，每次覆盖，已进 .gitignore
```

四层各管一件事，谁也不知道别人从哪拿的数据：`llm_client` 不知道自己在评什么，`agent` 不知道题从哪来，`judge` 不知道成绩怎么汇总，`run_eval` 只串流程。要换模型、换用例、换判分标准，各改各的。

判分器之间也互不知情：每个只认自己的判据，不引用别的维度。**只有维度 1 拿标准答案**——它是唯一真比对得数的；其余五维都不喂 `expect`，喂了会把裁判往「答案对不对」上引。

## 两个模型、两家厂商

| 角色 | 模型 | 温度 | 环境变量 | 接口 |
|---|---|---|---|---|
| 被测（答题） | `deepseek-chat` | 0.3 | `LLM_API_KEY` | `api.deepseek.com` |
| 判分（Judge） | `glm-5.3-flash` | 0 | `JUDGE_API_KEY` | `open.bigmodel.cn` |

分家的理由就一条：避开自我偏好偏差（self-preference）——不能让自己的同类判自己，否则它给高分往往是因为「风格像我」，不是因为答案对。

两个 key 都从环境变量读，不写进代码、不进仓库。

## 怎么跑

在**仓库根目录**用 `-m` 跑，不要 `cd` 进 `eval/`：

```bash
python -m eval.run_eval                        # 跑全部 19 条
python -m eval.run_eval --only hallucination   # 只跑某一维（键名见 JUDGES 分派表）
python -m eval.agent                           # 只测被测模型，看它怎么答一道题
python -m eval.judges.knowledge                # 只测判分器，喂一条已知算错的答卷
```

必须 `-m` 的原因：包内用的是 `from eval.agent import answer` 这类按包名的绝对导入。直接 `python eval/run_eval.py` 启动时，`eval` 不在搜索路径里，会报找不到模块。

## 输出：results.json

一条用例一个对象，七个字段：

| 字段 | 含义 |
|---|---|
| `id` | 用例编号，如 `hl-001` |
| `dimension` | 维度键，如 `hallucination` |
| `expect` | **语义分叉**：维度 1 存标准答案，维度 6 存期望判定（`fail` 等）；其余五维是旧字段，判分器已不读 |
| `answer` | 被测模型的作答原文（多轮只存最后一轮） |
| `verdict` | `pass` / `partial` / `fail` |
| `error_type` | 该维度约定的错误类型，或 `null` |
| `reason` | 判分器给的一句话理由 |

存 `answer` 是为了事后回查：判分器说「得数正确」，得能翻出原文看它到底算对没有。只存结论的话，判错了也查不出来。

末尾还会打印一句 `N条用例，M条通过`——**这一行对判分器自检用例没有意义**：它们的期望本来就多是 `fail`／`partial`，`0 pass` 反而是对的。验收要看 `results.json` 里每条 `verdict` 是否等于该用例的期望判定，不是看这行数字。统计口径第 29 天改（见 `docs/ai-eval-notes.md` 第九节第 1 条）。

## 三档怎么分（维度 1：知识点正确性）

- **`pass`**：得数正确，引用的定理、公式名称也对。
- **`partial`**：得数对但定理用错（属于蒙对）；或者方法对、中间步骤对，只是最后一步得数抄错。
- **`fail`**：得数错且过程也错，或引用了根本不存在的定理。

这个档位只判「知识点正确性」一件事。步骤跳不跳、讲没超纲、讲深讲浅、话说得长不长，都不在这一维扣分——那是维度 2、3、4 的事。

## 已知问题（都还没修）

1. **多轮只存末轮**。判分器已经拿到整串 `replies`（维度 5 逐轮判），但 `results.json` 的 `answer` 仍只存 `replies[-1]`，第 1 轮原话查不到。改法两条（改存档结构 / 要求判分器在 `reason` 里逐轮写），定在第 29 天。
2. **`reason` 偶有复读档位定义**。第 26 天已在维度 2 的 prompt 里加「点名答卷里的具体一步」，坑 1、坑 2 仍记为未修，验收时按「连跑两遍理由不该相同」看。
3. **统计行只数 `pass`**。六个维度的期望大多不是 `pass`（19 条里只有 6 条期望 `pass`），所以那行数字必然误导。见上节说明与第九节第 1 条。
4. **没有历史**。`results.json` 每次覆盖，跨天对比无从谈起。

## 相关文档

- `docs/eval-dimensions.md` —— 六个维度：判什么、用什么判、判定标准、失败样例、覆盖计划
- `docs/ai-eval-notes.md` —— LLM-as-Judge 原理、各维实测记录（8.1—8.17）、待定集中登记（第九节）
- `docs/eval-pitfalls.md` —— 踩坑佐证（面试用「问题 → 怎么发现 → 根因 → 怎么修」四步讲）
- `docs/curriculum-reference.md` —— 教材知识点清单（维度 3 的扫描底稿；维度 6 已不再使用）
