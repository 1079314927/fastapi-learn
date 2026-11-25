#`agent` 不知道题从哪来
from eval.llm_client import chat

SYSTEM_PROMPT="你是一名初中数学教师，能够给七年级到九年级的学生答疑，讲题时逐步讲解，不是只给答案。"
def answer(turns:list[str])->list[str]:
    messages=[{"role":"system","content":SYSTEM_PROMPT}]
    replies=[]

    for t in turns:
        messages.append({"role":"user","content":t})
        reply=chat(messages,temperature=0.3)
        messages.append({"role":"assistant","content":reply})
        replies.append(reply)

    return replies

if __name__=="__main__":
    for i, r in enumerate(answer(["解方程2x+3=7"]),1):
        print(f"第{i}轮：\n{r}\n")  