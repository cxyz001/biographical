# 前端与全栈学习实验

教程：[前端零基础到全栈工程实战](../08-前端零基础到全栈工程实战.md)。

建议使用仍受维护的 Node.js LTS，不安装第三方包。本机实际验证版本为 Node.js 20.12.0，4 项测试通过；该旧版本不是生产部署推荐版本。从仓库根目录运行自动测试：

```bash
node --test JD/frontend-learning/ticket-service.test.mjs
```

手动运行（用完 Ctrl+C 停止）：

```bash
node JD/frontend-learning/ticket-service.mjs
```

浏览器访问 `http://127.0.0.1:3088/api/tickets`，初始返回空列表。这是接口实验，没有网页 UI。PowerShell 测试创建和修改：

```powershell
Invoke-RestMethod http://127.0.0.1:3088/api/tickets -Method Post -ContentType application/json -Body '{"title":"Repair pump"}'
Invoke-RestMethod http://127.0.0.1:3088/api/tickets/1 -Method Patch -ContentType application/json -Body '{"version":1,"status":"done"}'
Invoke-RestMethod http://127.0.0.1:3088/api/tickets/1 -Method Patch -ContentType application/json -Body '{"version":1,"status":"open"}'
```

最后一条预期 409，并非实验失败。重新 GET 查看 version=2。重复运行创建命令会增加 ID，重启服务会清空数据。端口占用时可在 PowerShell 中先设 `$env:PORT='3089'` 再启动。

4 项 HTTP 集成测试覆盖 CRUD 子集、同版本并发冲突、输入校验与服务端字段控制、请求大小与资源不存在。单进程 Map 的原子更新只用于解释乐观并发控制；生产应换成数据库条件 UPDATE，补齐认证、租户隔离、持久化、审计、分页和速率限制。

这里没有实现 CORS、登录或完整 OpenAPI；浏览器跨端口调用会涉及同源策略，可用开发代理或同源 BFF。正文的 React/Vue/SQL/SSE 片段是对应章节练习，需要按项目上下文组装。

`research.py` 可重跑 GitHub 搜索和资料读取；`search-results.json`、`sources.json` 保留实际结果与读取哈希。它们不是依赖锁文件，项目实施仍应固定版本与提交。
