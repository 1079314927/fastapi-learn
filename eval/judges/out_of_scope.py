"""judges/out_of_scope.py —— 维度 3：超纲检测

职责：先用规则扫一遍答卷，把「出现了哪些越界词」写成证词，
再连同题目、年级、作答一起交给裁判模型，由它判断这些词落在主线还是旁注。
规则只负责找得全，档位由模型定。
"""
import json
import os

from eval.llm_client import chat

from eval.judges.knowledge import JUDGE_API_URL,JUDGE_MODEL


JUDGE_SYSTEM_PROMPT = """你是评测判分员，不是老师，不给学生讲题。
只判「解题方法有没有超出初中课程范围」这一件事。知识点算得对不对、步骤全不全、用词是否形式化、讲得深浅、措辞长短，都不在本维度扣分。

超纲不是「难」，是「越出范围」：结论可能对、步骤也合理，但用的是初中学生没学过的东西，他照着这句话做不下去。

判断分两关，顺序不能倒：先判越界没越界，再判位置。

第一关，判越界。看学生卡在哪一层：
- 卡在认字：答卷的推理用了该年级没有的数学符号或记号体系来承载（如 mod 7、a ≡ b (mod 7) 这类同余式，f'(x)、dy/dx，∑、∫，n!，C(n,m)、A(n,m)，矩阵括号，向量箭头）。这算越界。学生看不懂的不是它的意思，是这个写法本身，他从没学过怎么读，照着也抄不下去。这一类不再问「能不能翻译成大白话」。
- 卡在概念：答卷用了该年级没有的数学对象或解法（如导数、求导、积分、极限、无穷、复数、虚数、向量、矩阵、行列式、等差数列、等比数列、通项公式、均值不等式、柯西、洛必达、泰勒、概率密度、同余与模运算）。这算越界。也包括一个符号都没写、但思路本身如此的情形（如「函数值在变化率最快的地方取到最小」）。
- 卡在说法：答卷只用了该年级没有的中文词语，但指的是初中已经学过的同一个操作（如「由同解原理，两边同时减 3」指的是两边都减 3；「首项系数非零」指的是 x 前面那个数不能是 0）。这类不算方法越界，本维度不扣分。

注意：最后这条豁免只适用于中文词语。凡是符号、记号、公式写法，一律按第一条处理，不适用豁免。

第二关，判位置。只对已经判定越界的答卷判：
- 越界内容出现在解题主线，学生绕不开 → fail。
- 越界内容只在旁注（如结尾一句「其实用导数更快，等你高中会学」），删掉不影响学生照着做 → partial。
- 没有越界内容 → pass。

下面这些是初中内容，答案里出现属于正常，不要当成越界：
√、Δ（判别式）、求根公式、韦达定理、sin/cos/tan（限直角三角形锐角）、π、配方法、因式分解、十字相乘、一次函数、二次函数、反比例函数、相似、全等、圆、扇形、勾股定理。

关于【规则扫描结果】：那是机器扫出的「答卷里出现过哪些可能越界的词」，只说明这些词出现过，不说明它们在句子里起什么作用。
- 命中不等于越界：同一个词可能落在旁注里，也可能只是顺口一提。
- 零命中也不等于安全：可能是思路越界，但一个符号都没写。
所以扫描结果只当线索，档位由你读完答卷后自己定。

只输出一个 JSON 对象，不要任何额外文字，不要代码块标记：
{"verdict":"pass 或 partial 或 fail","reason":"一句话","error_type":"out_of_scope_mention 或 out_of_scope_method 或 null"}
"""



BLACKLIST=[
    "∫", "∑", "lim", "d/dx", "f'(x)", "dy/dx",
    "ln", "lg", "log_", "√-1", "i²=-1",
    "[[", "C(n", "A(n", "n!", "→",
    "导数", "求导", "积分", "极限", "无穷",
    "复数", "虚数", "向量", "矩阵", "行列式",
    "等差数列", "等比数列", "通项公式",
    "均值不等式", "柯西", "洛必达", "泰勒", "概率密度",
]

# ---------- 允许清单：初中范围内的，规则不许误伤 ----------
# 只用来当自检靶子，不参与 scan 的过滤逻辑
ALLOWLIST = [
    # 符号类（6 个）
    "√", "Δ", "π", "sin", "cos", "tan",
    # 名词类（13 个）
    "求根公式", "韦达定理", "配方法", "因式分解", "十字相乘",
    "一次函数", "二次函数", "反比例函数", "勾股定理",
    "相似", "全等", "圆", "扇形",
]

def scan(text):
    hits=[]
    for w in BLACKLIST:
        if w in text:
            hits.append(w)
    return hits

def judge(case: dict, replies: list[str]) -> dict:
    """返回形如 {"verdict": "pass", "reason": "...", "error_type": null} 的字典。"""
    hits = scan(replies[-1])
    #"、".join(hits):从列表里取出元素，在它们之间插入你指定的符号，直接连成一个新字符串。
    evidence = "、".join(hits) if hits else "（无命中）"#Python 判断真假时，空列表算「假」，非空列表算「真」
    user_prompt = (
        "【题目】" + case["turns"][-1] + "\n"
        "【标准答案】" + case["expect"] + "\n"
        "【被测模型的作答】" + replies[-1]+ "\n"
        "【规则扫描结果】命中的越界词："+ evidence

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
    result["source_layer"]= "rule_hit" if hits else "no_hit"
    return result

if __name__=="__main__":
    print(scan("用向量做相对运动"))
    print(scan("对 f(x) 求导，f'(x)=2x-6"))
    print(scan("9x+4=7x-3"))

    #测「清单本身有没有被写脏」
    for w in ALLOWLIST:
        assert scan(w)==[],f"误伤:{w}"
    # 真调用验证：一条该判 pass（规则零命中），一条该判 fail（规则命中）
    demo_pass = {
        "id": "demo-pass",
        "turns": ["解方程 x² - 2x - 1 = 0"],
        "expect": "x = 1 ± √2",
    }
    print(judge(demo_pass, ["用求根公式，Δ = 4 + 4 = 8，x = (2 ± √8)/2 = 1 ± √2。"]))

    demo_fail = {
        "id": "demo-fail",
        "turns": ["求 y = x² - 6x + 5 的最小值"],
        "expect": "-4",
    }
    print(judge(demo_fail, ["对 f(x) 求导，f'(x) = 2x - 6，令其为 0 得 x = 3，代入得最小值 -4。"]))

