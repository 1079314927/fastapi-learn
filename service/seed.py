from models import Question
from database import SessionLocal



QUESTIONS=[
    {
        "question":"解方程 x² - 5x + 6 = 0",
        "knowledge_point":"一元二次方程-因式分解法",
        "steps":"1. 找两个数，乘积为 6、和为 -5，即 -2 和 -3\n2. 写成 (x-2)(x-3)=0\n3. 令每个括号分别等于 0：x-2=0 或 x-3=0\n4. 得 x=2 或 x=3",
        "common_mistake":"凑数时只看乘积不看和，写成 (x+2)(x+3)；或只写出一个解，忘了两个括号都要等于 0",
    },
    {
        "question":"解分式方程 2/(x-1) = 3/x",
        "knowledge_point":"分式方程-交叉相乘",
        "steps":"1. 交叉相乘：2x = 3(x-1)\n2. 展开：2x = 3x - 3\n3. 移项得 x = 3\n4. 检验：x=3 时两个分母都不为 0，成立",
        "common_mistake":"写完解不检验，把使分母为 0 的增根留下；交叉相乘时漏乘某一项",
    },
    {   "question":"求二次函数 y = x² - 4x + 3 的顶点坐标和最小值",
        "knowledge_point":"二次函数-配方法",
        "steps":"1. 配方：y = (x-2)² - 1\n2. 顶点式 y=(x-h)²+k 中 h=2、k=-1，顶点 (2,-1)\n3. 开口向上（x² 系数为正），最小值是 -1",
        "common_mistake":"顶点横坐标符号抄反，写成 (-2,-1)；配方时把 -4 的一半 -2 的平方漏掉",
    },
    {
       "question": "直角三角形两条直角边为 6、8，求斜边；若斜边为 13、一条直角边为 5，求另一条直角边",
        "knowledge_point": "勾股定理",
        "steps": "1. 第一问：6²+8²=36+64=100，斜边 = √100 = 10\n2. 第二问：13²-5²=169-25=144，另一直角边 = √144 = 12",
        "common_mistake": "把斜边当直角边代进 a²+b²=c²；开方后只写负数解或漏写单位",
    },
    {
        "question": "解不等式组 2x-1 > 3 且 x+2 ≤ 5",
        "knowledge_point": "一元一次不等式组",
        "steps": "1. 解第一个：2x > 4，x > 2\n2. 解第二个：x ≤ 3\n3. 取交集：2 < x ≤ 3",
        "common_mistake": "数轴上边界开闭搞混（2 不取、3 要取）；两边同乘除负数时忘记改变不等号方向",
    }
]


def main():
    db=SessionLocal()
    db.add_all([Question(**item) for item in QUESTIONS])
    db.commit()
    db.close()
    print("插入完成",len(QUESTIONS),"条")

if __name__=="__main__":
    main()