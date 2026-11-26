"""judges/knowledge.py —— 维度 1：知识点正确性（Judge 为主）

职责：拿 题目 + 标准答案 + 被测模型的作答，交给裁判模型，要回一个结构化判定。
它不知道题目从哪来，也不知道成绩怎么汇总。
"""

import json
import os

from eval.llm_client import chat

JUDGE_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
JUDGE_MODEL = "glm-5.3-flash"

JUDGE_SYSTEM_PROMPT = """你是评测判分员，不是老师，不给学生讲题。
只判「知识点正确性」这一件事。步骤完整度、是否超纲、讲得深浅、措辞长短，都不在本维度扣分。

分档：
- pass：得数正确，引用的定理、公式名称也对。
- partial：得数对但定理或公式用错，属于蒙对；或方法正确、中间步骤正确、只是最后得数抄错。
- fail：得数错且过程也错，或引用了不存在的定理。

只输出一个 JSON 对象，不要任何额外文字，不要代码块标记：
{"verdict":"pass 或 partial 或 fail","reason":"一句话","error_type":"method_error 或 final_answer_error 或 knowledge_error 或 null"}
"""


def judge(case: dict, replies: list[str]) -> dict:
    """返回形如 {"verdict": "pass", "reason": "...", "error_type": null} 的字典。"""
    user_prompt = (
        "【题目】" + case["turns"][-1] + "\n"
        "【标准答案】" + case["expect"] + "\n"
        "【被测模型的作答】" + replies[-1]
    )

    raw = chat(
        [{"role": "system", "content": JUDGE_SYSTEM_PROMPT},
         {"role": "user", "content": user_prompt}],
        model=JUDGE_MODEL,
        temperature=0,
        api_key=os.getenv("JUDGE_API_KEY"),
        api_url=JUDGE_API_URL,
    )

    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    result = json.loads(raw)
    if result["error_type"] == "null":
        result["error_type"] = None
    return result


if __name__ == "__main__":
    demo_case = {
        "id": "demo",
        "turns": ["一个数的 3 倍加 2 等于 8，求这个数。"],
        "expect": "2",
    }
    demo_replies = ["设这个数为 x，3x+2=8，3x=6，x=3。所以这个数是 3。"]
    print(judge(demo_case, demo_replies))
