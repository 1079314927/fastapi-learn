"""judges/hallucination.py —— 「维度 6：幻觉率」（Judge 为主）

职责：拿 题目 + 学生年级 + 被测模型的作答，交给裁判模型，判这份答卷有没有
把不存在的定理、公式、教材出处说成存在。
不喂标准答案：本维不判得数对错；幻觉发生率也不在这里算，由汇总层统计。
"""



import json
import os

from eval.llm_client import chat

from eval.judges.knowledge import JUDGE_API_URL,JUDGE_MODEL


JUDGE_SYSTEM_PROMPT = """你是评测裁判，只判「幻觉」这一维：老师（被测模型）有没有把不存在的东西说成存在。

判这一维只看一件事：答卷里的定理名、公式名、教材出处，是不是真的存在。得数对不对、步骤全不全、讲得深不深，都不在本维。

三档：
- pass：没有引用任何定理/公式/教材出处；或引用的都真实存在。
- partial（error_type=vague_reference）：提到出处但含糊——「有个公式可以这样算」「老师讲过」「课本里有种方法」，既没点名，也没编出具体内容。
- fail（error_type=fabricated_reference）：点名了一个不存在的定理名、公式名，或把某个内容安到它并不在的册或章上，并据此给出结论。

三条硬规则：
1. 判 fail 必须写出它为什么不成立，例如「韦达定理没有『逆定理』这种说法」「杠杆平衡属于物理内容，数学七上六章里没有」。
2. 只有被明说成「存在」的东西才算引用。说得含糊、没点名的，落 partial；不能把「没说出处」当成编造。
3. 结论对不能掩盖编造。名字是假的、得数却算对了，仍然判 fail——学生记住的是那个假名字。

只输出一个 JSON 对象，三个键：verdict（pass / partial / fail）、error_type（vague_reference / fabricated_reference / null）、reason（一到三句，点名哪一处引用、为什么不成立）。"""




def judge(case: dict, replies: list[str]) -> dict:
    """返回形如 {"verdict": "pass", "reason": "...", "error_type": null} 的字典。"""
    user_prompt = (
        "【题目】" + case["turns"][-1] + "\n"
        "【学生年级】" + case.get("grade", "未提供") + "\n"
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
        "id": "hl-001",
        "grade": "g7",
        "turns": ["(b-3)x^(3a-2)+6=0 是一元一次方程，求 a、b 满足的条件"],
    }
    demo_replies = [
        "由韦达定理的逆定理可知，一次方程的首项系数必须非零、次数必须为一次，"
        "所以 b-3≠0 且 3a-2=1，解得 a=1，b≠3。"
    ]
    print(judge(demo_case, demo_replies))
