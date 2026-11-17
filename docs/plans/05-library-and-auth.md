# 素材覆盖、列表详情与个人鉴权实施计划

状态：三项代码已实现，本地套件与前端生产构建通过。真实 OAuth 和网页端到端验收待配置；浏览器工具当前不可用。沿用 main，不另建工作树、不提交或部署；未修改用户环境文件或数据库 schema。

## 设计与目录

- storage.py：按身份插入或锁定已有文章；指纹相同返回 duplicate，否则在同一事务更新字段、删除旧分块、写入新分块，返回 updated，保留 ID 与首次创建时间。
- documents.py／main.py：增加 GET /documents（limit／offset 有界分页）和 GET /documents/{id}（正文、元数据及有序分块）。详情用一个数据库语句读取文章和分块，避免覆盖期间读到不同版本。
- 新增 topic_agent/auth.py：Authlib OAuth、Starlette 签名会话，固定 GitHub 提供方，state 与 PKCE；通过 /user 核对配置的数字 ID；读写接口验证签名会话与绝对到期时间，写请求再校验 Origin。配置缺失返回 503，不提供开发绕过。
- apps/web/app：新增 library/page.tsx、library/[id]/page.tsx、login/page.tsx、components 与 lib 目录。components 放会话门禁和导航；lib 放前端请求辅助。所有私有数据由受保护 API 获取，未登录页面不加载素材。代理转发 Cookie，页面不接触 token 或数据库凭据。
- 延续现有蓝灰背景、衬线标题、蓝色主操作；列表用可扫描条目，详情正文用保留换行的纯文本，不直接渲染用户 HTML。

## 步骤与验收

1. 先修改数据库测试：新增／重复／覆盖、覆盖后分块数量减少、更新失败恢复原文与旧分块；运行真实测试看到旧代码失败，再实现并重跑。测试使用独立随机来源及回滚，不改用户文章。
2. 增加列表／详情查询与测试：分页、空列表、不存在 ID、有序分块，正文含 HTML 时页面按文本显示。
3. 安装 Authlib、HTTPX、itsdangerous（现有 FastAPI 不提供 OAuth 协议和 Cookie 签名）；使用官方 OAuth 客户端避免自行实现协议。增加未登录、错误账号、篡改／过期会话、跨站写入、回调失败、注销测试；只模拟外部 GitHub 网络，不宣称真实 OAuth 已验收。
4. 页面接入列表、详情、登录、注销与上传 updated 结果；运行后端套件、真实数据库测试及前端构建，能访问浏览器时再核对界面。
5. 文档列出用户需配置的变量、GitHub OAuth 回调地址和未完成的真实登录验收。下一步配置后实际登录、上传覆盖与查看，部署仍需授权。

## 运行边界

- 单用户素材库，不添加用户表或完整 RBAC。GitHub 数字 ID 是唯一允许账号。
- 后端 APP_URL 是前端固定来源，例如 http://localhost:3000；回调固定为 APP_URL/backend/auth/callback，不信任请求中的 Host 决定回调。
- 线上 Cookie Secure；HttpOnly、SameSite=Lax，最长８小时。注销清除当前浏览器 Cookie，已被窃取的副本在到期前不能主动撤销；紧急情况下轮换 SESSION_SECRET 使旧签名失效。
- .env.local 不由助手修改。无真实 OAuth 凭据时仍完成代码和隔离测试，但明确保留真实 GitHub 登录验收。

官方依据：GitHub OAuth 文档 https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps 、Authlib Starlette 客户端源码 https://github.com/authlib/authlib/blob/main/authlib/integrations/starlette_client/apps.py 、Starlette SessionMiddleware https://starlette.dev/middleware/#sessionmiddleware 。
