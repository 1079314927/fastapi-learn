#`run_eval` 只负责串联

#从题库找题，交给answer函数（AI教师），拿到教师提供的答案
import json
from pathlib import Path

from eval.agent import answer
from eval.judges.knowledge import judge
from eval.judges.step_consistency import judge as step_judge
from eval.judges.out_of_scope import judge as oos_judge
from eval.judges.level_matching import judge as lm_judge
from eval.judges.multi_turn import judge as mt_judge
from eval.judges.hallucination import judge as hl_judge



import argparse
parser=argparse.ArgumentParser()#造一个解析器
parser.add_argument("--only",default=None)
args=parser.parse_args()#读命令行，返回Namespace(only=None)/Namespace(only='knowledge')
print("本次只跑：",args.only)

cases=[]
for path in Path("eval/cases").glob("*.json"):
    with open(path,"r",encoding="utf-8")as f:
        cases.extend(json.load(f))

JUDGES={
    "knowledge":judge,
    "step_consistency":step_judge,
    "out_of_scope":oos_judge,
    "level_matching":lm_judge,
    "multi_turn": mt_judge,
    "hallucination":hl_judge

}

if args.only is not None and args.only not in JUDGES:
    raise ValueError(f"--only 给的维度 {args.only} 不在分派表里")
    #必须输入None或者在分派表里面的键

result=[]
for c in cases:
    if args.only is not None and c["dimension"] != args.only:
        #是None或者就是筛选出来的维度才能继续往下跑
        continue

    if "canned_reply" in c:
        raw=c["canned_reply"]
        replies=raw if isinstance(raw, list) else [raw]

        print(f"固定答卷：{c['id']}")
    else:
        replies=answer(c["turns"])
        print(f"{c['id']} 作答完成，{len(replies[-1])} 字。")

    dimension=c["dimension"]
    if dimension not in JUDGES :
        raise ValueError(f"用例{c["id"]}的dimension是{dimension}，分派表里没有这个键。")
    judge_fn=JUDGES[dimension]
    verdict=judge_fn(c,replies)
    result.append({"id":c["id"],
                   "dimension":c["dimension"],
                   "expect":c["expect"],
                   "answer":replies[-1],
                   "verdict":verdict["verdict"],
                   "error_type":verdict["error_type"],
                   "reason":verdict["reason"]})

passed=0
for r in result:
    if r["verdict"]=="pass":
        passed += 1
print(f"{len(result)}条用例，{passed}条通过")

with open("eval/results.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
