"""judges/level_matching.py —— 「维度 4：分层讲解匹配（按年级分档）」（Judge 为主）

职责：拿 题目 + 学生年级 + 被测模型的作答，交给裁判模型，要回一个结构化判定。
它不知道题目从哪来，也不知道成绩怎么汇总。
"""


import json
import os

from eval.llm_client import chat

from eval.judges.knowledge import JUDGE_API_URL,JUDGE_MODEL


JUDGE_SYSTEM_PROMPT = """你是评测判分员，不是老师，不给学生讲题。

只判一件事：这份讲解的深度、术语密度、步骤颗粒度，是否匹配提问学生的年级。
内容对不对、步骤全不全、方法是否超纲、字数长短、排版好不好看，都不在本维度扣分。

先看【学生年级】。它指提问学生所在的年级，不是题目所属的年级。按该年级学过的范围判：
- g7 初一：有理数、整式、一元一次方程、不等式、几何图形初步、相交线与平行线、实数、二元一次方程组、数据的收集整理
- g8 初二：三角形、全等、轴对称、整式乘法与因式分解、分式、二次根式、勾股定理、平行四边形、一次函数、数据的分析
- g9 初三：一元二次方程、二次函数、旋转、圆、概率初步、相似、锐角三角函数、投影与视图

分档：
- pass：术语都在该年级范围内，步骤颗粒度与之匹配。
- partial：略高于该年级，但当场的解释让人接得住（用了高年级的词，却用该年级听得懂的话说明了）；或者讲得比该年级需要的浅一档，把学生早就会的东西又讲一遍。
- fail：明显超出该年级，且没有解释，学生根本接不住。

`partial` 与 `fail` 的分界：术语是装饰，还是承载关键信息。
- 术语只是装饰，后面已经用该年级听得懂的话把同一件事说清 → partial。
- 术语承载学生必须懂的信息，却不作解释（不认得这个词就推不下去）→ fail。

一条硬规则：讲得太浅，最差只能判 partial，绝不判 fail。给基础薄弱的学生从头讲一遍是负责，只是对普通学生显得啰嗦。它落在 pass 与 partial 之间，看学生基础。

判断时守住三条：
1. 「听不懂」是 fail，「听懂了但费劲」是 partial，「太啰嗦」也是 partial。这三件事差得很远：啰嗦只是费时间，听不懂是白讲。
2. 简洁不等于讲太浅。又正确又干净的短答案判 pass，不要因为「不够漂亮」「太简单」就判 partial。
3. 方法本身是否超出该年级，不在本维度扣分；只有当这套讲法让学生接不住时，才在本维度扣。

reason 必须点出答卷里的具体那句话或那个词，不许复述档位定义。

错误类型：
- 判 partial 且略深但讲通了 → slightly_advanced
- 判 partial 且讲得太浅 → too_shallow
- 判 fail → mismatch_advanced
- 判 pass → null

只输出一个 JSON 对象，不要任何额外文字，不要代码块标记：
{"verdict":"pass 或 partial 或 fail","reason":"一句话，点出答卷里的具体表述","error_type":"slightly_advanced 或 too_shallow 或 mismatch_advanced 或 null"}
"""



def judge(case: dict, replies: list[str]) -> dict:
    """返回形如 {"verdict": "pass", "reason": "...", "error_type": null} 的字典。"""
    user_prompt = (
        "【题目】" + case["turns"][-1] + "\n"
        "【学生年级】" + case["grade"] + "\n"
        "【被测模型的作答】" + replies[-1]
    )

    raw = chat(
        [{"role": "system", "content": JUDGE_SYSTEM_PROMPT},
         {"role": "user", "content": user_prompt}],
        model=JUDGE_MODEL,
        temperature=0,
        api_key=os.getenv("JUDGE_API_KEY"),
        api_url=JUDGE_API_URL,
        response_format={"type": "json_object"},
    )

    body = raw.strip()
    try:
        result = json.loads(body)
    except json.JSONDecodeError:
        print("解析失败 | 裁判原始返回 =", repr(raw))
        raise

    if result["error_type"] == "null":
        result["error_type"] = None
    return result


if __name__ == "__main__":
    demo_fail = {
        "id": "demo-fail",
        "turns": ["若关于 x 的方程 (b-3)x^(3a-2)+6=0 是一元一次方程，求 a、b 满足的条件。"],
        "expect": "a=1，b≠3",
        "question_type": "calc",
        "grade": "g7",
    }
    print(judge(demo_fail, ["由首项系数非零，得 b≠3；次数指标须满足线性约束 3a-2=1，故 a=1。所以 a=1 且 b≠3。"]))

    demo_partial = {
        "id": "demo-partial",
        "turns": ["解方程 2x + 3 = 7"],
        "expect": "x=2",
        "question_type": "calc",
        "grade": "g7",
    }
    print(judge(demo_partial, ["由一元一次方程的同解原理，等式两边同时减去 3，得 2x = 4，再同时除以 2，得 x = 2。"]))

    demo_pass = {
        "id": "demo-pass",
        "turns": ["解方程 2x + 3 = 7"],
        "expect": "x=2",
        "question_type": "calc",
        "grade": "g7",
    }
    print(judge(demo_pass, ["把 3 移到右边变成 -3，2x = 7 - 3 = 4，所以 x = 2。"]))

