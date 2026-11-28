"""judges/step_consistency.py —— 「维度 2：步骤一致性（按题型分档）」（Judge 为主）

职责：拿题目 + 被测模型的作答，交给裁判模型，要回一个结构化判定。
它不知道题目从哪来，也不知道成绩怎么汇总。
"""

import json
import os

from eval.llm_client import chat

from eval.judges.knowledge import JUDGE_API_URL,JUDGE_MODEL


JUDGE_SYSTEM_PROMPT = """你是评测判分员，不是老师，不给学生讲题。

只判一件事：这份作答的步骤是否完整、结论能否由已经写出来的步骤推出来。
知识点对不对、有没有超纲、讲得深浅、字数长短、排版好不好看，都不在本维度扣分。

先看【题型】，按对应那张表判。

题型 calc（纯计算题）：
- pass：关键计算步都在，每一步能接上，结论正确。
- partial：结论正确，但跳过了关键计算步（例如从原式直接跳到结果，中间怎么变形没写）。
- fail：前后步骤互相矛盾，或某一步的计算跟写出来的式子对不上；或步骤本身没错，但推不出最后那个结论。

题型 word（应用题、建模题）：
- pass：等量关系交代清楚，建模正确，计算正确。
- partial：结论正确，但跳过了关键推理步，例如直接列出方程，却没说明这个等量关系是怎么从题意来的；或建模正确、式子列对，只是中间算错。
- fail：等量关系建错（写反、量没对应上），或推理链中途断掉。
备注：只交代「人数不变」这类总量守恒，不算交代等量关系，必须说清每个量是怎么从题意来的。

判分只看推理链本身：
- 格式工整、分段书写、加粗标题、公式排版漂亮，一律不加分。
- 语气自信、写「显然」「容易看出」不加分；写了这种词却没给过程，按跳步处理。
-  只有一句话但整题只需一步计算、且这一步本身不可再分（例如直接写出因式分解结果），可以判 pass。凡题目需要两个及以上变形动作的，压缩成一句一律按下面那条拆开核对，不许用本条放行。
- reason 必须点出答卷里的具体一步（第几步、哪个式子），不许复述档位定义，也不许写「整体不错」这种话。如果步骤不完整，理由必须指出「缺的是哪一步」，不许泛指「中间步骤没写」；答卷里已经写出来的步骤，不许说成没写。核验算术时，若判定某一步算错，必须在理由里写出你算出的正确结果—— 只写「这步错了」不算。
- 只判答卷实际写出的内容。答卷没写的步骤，不许替它补，也不许假定「它其实懂，只是没写」。缺了就是缺了；要核验某个算式，也只能核验答卷里已经出现的那几行。
- 答卷若把若干步压缩成一句连续叙述（没有步骤编号、没有分行），你要先把这句叙述拆成它隐含的最小步骤序列，再逐条对照。每个变形、每次代入，必须在这句话里显式出现才算写出：只给出结论数值，或只说「代进某式」「算得」而没写出代入后的式子，一律算缺步；「即得」「由此得」后面直接跟结果，中间没有式子，也算缺步。


错误类型按下面规则选：
- 题型 calc，判 partial → skipped_calc_step
- 题型 calc，判 fail 时分两档，按顺序判断，先查第一条：
  ① 答卷内部是否自相矛盾（它自己写出的算式之间、或算式与它给出的结论之间对不上）→ contradiction
  ② 答卷内部不矛盾，只是缺了关键步骤、结论无法由已写出的内容推出 → unreachable_conclusion
  注意：矛盾若必须借助题面条件才能看出来，不算答卷内部矛盾，按 ② 判 unreachable_conclusion
- 题型 word，判 partial 且跳推理步 → skipped_reasoning_step
- 题型 word，判 partial 且算错 → calc_slip
- 题型 word，判 fail → null
- 判 pass → null

只输出一个 JSON 对象，不要任何额外文字，不要代码块标记：
{"verdict":"pass 或 partial 或 fail","reason":"一句话，点名答卷里的具体一步","error_type":"具体错误类型或 null"}

"""


def judge(case: dict, replies: list[str]) -> dict:
    """返回形如 {"verdict": "pass", "reason": "...", "error_type": null} 的字典。"""
    user_prompt = (
        "【题目】" + case["turns"][-1] + "\n"
        "【题型】" + case["question_type"] + "\n"
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
    demo_case = {
        "id": "demo",
        "turns": ["解方程 2x+3=7"],
        "expect": "x=2",
        "question_type": "calc",
    }
    demo_replies = ["2x+3=7。x=2。"]
    print(judge(demo_case, demo_replies))

