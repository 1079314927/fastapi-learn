#`run_eval` 只负责串联

#从题库找题，交给answer函数（AI教师），拿到教师提供的答案
import json
from eval.agent import answer
from eval.judges.knowledge import judge

with open("eval/cases/knowledge.json","r",encoding="utf-8")as f:
    cases=json.load(f)

result=[]
for c in cases:
    replies=answer(c["turns"])
    print(f"题目的id是：{c['id']}，答案是{replies}。")
    verdict=judge(c,replies)
    result.append({"id":c["id"],
                "verdict":verdict["verdict"],
                "error_type":verdict["error_type"],
                "reason":verdict["reason"]})
print(result)

passed=0
for r in result:
    if r["verdict"]=="pass":
        passed += 1
print(f"{len(result)}条用例，{passed}条通过")

with open("eval/results.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
