# User Todo API — 接口自动化测试框架

基于 **AOM（API Object Model）** 三层架构设计的接口自动化测试项目。

## 架构设计
```
client/   第一层：HTTP 基础设施（Session、重试、日志）
api/      第二层：API Object 封装（URL、请求体、响应解析集中管理）
tests/    第三层：测试用例（只写业务断言，零 URL 字符串）
```

## 核心设计决策

- **为什么用 AOM 而不是直接写 requests**：端点 URL 集中在 api/ 层管理，
  URL 变更只改一处，所有用例自动修复
- **Schema 验证放在 API Object 层内部**：保证每次调用都做契约验证，
  测试用例只写业务语义断言
- **scope="class" fixture**：同一测试类共享预置数据，减少重复创建开销，
  yield 保证清理逻辑在任何情况下都执行

## 快速开始
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
pytest
```

## 测试覆盖

| 场景           | 用例数 |
|----------------|--------|
| 用户 CRUD      | 11     |
| Todo CRUD      | 8      |
| 跨资源约束     | 2      |
| 幂等性验证     | 1      |
| 参数过滤验证   | 1      |
| 负向 / 边界    | 6      |