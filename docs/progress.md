# 进度台账

> 更新时间：2026-11-23
> 这份台账只回答一个问题：**这个仓库做到哪了**。个人学习进度记在别处（Obsidian），两边不混写。

## 当前阶段

- 阶段一：服务底座 + 测试 + CI —— **已完成**
- 阶段二：AI 评测层 —— **未开始**

## 当前进度

- Day 1—19：已完成
- Day 20：已完成（README / 架构图 / 台账）
- Day 21：未开始（阶段一收尾）
- 阶段二：0%

## 已完成

- **服务**：`POST /ask`、`GET /history`、`GET /health` 三个接口；MySQL 落库；题库 seed 5 条
- **容错**：超时 5 秒（`connect_timeout` / `pool_timeout`）；重试最多 2 次、只重试 `2003 / 2006 / 2013`；`X-Request-ID` 幂等（进程内 `_CACHE` + 数据库唯一索引两层）
- **日志**：结构化输出，每条带 `request_id` / 路径 / 耗时 / 状态
- **测试**：25 条（接口 23 + 单元 2），产出 Allure 报告
- **CI**：GitHub Actions 每次 push 到 main 自动跑，产物上传 artifact；故意改坏断言能变红（验证过）
- **文档**：`README.md`、`architecture.md`、`resilience.md`、`test-design.md`，以及本文件

## 未完成

- **阶段一收尾**：写 `docs/stage1-review.md`、冻结 `service/`、打 tag `v0.1-stage1-done`
- **阶段二：AI 评测层**：6 个维度 + LLM-as-Judge 最小实现 + 5 条失败用例佐证

## 下一步

Day 21：写 `docs/stage1-review.md`（五节）→ 冻结 `service/`（除测试暴露的 bug，不再改接口和表结构）→ 打 tag `v0.1-stage1-done` 并推送。
