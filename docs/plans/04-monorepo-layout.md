# 轻量 monorepo 目录迁移计划

用户已批准目录调整、本地提交与 push。本次仅移动文件和修正路径，不扩展业务功能，不安装依赖，不部署或修改数据库。

## 迁移映射

| 原路径 | 新路径 |
|---|---|
| topic_agent/ | apps/api/topic_agent/ |
| tests/ | apps/api/tests/ |
| requirements.txt | apps/api/requirements.txt |
| exercises/ | learning/python/exercises/ |
| docs/local/ | learning/python/notes/ |
| docs/imgs/ | learning/python/notes/imgs/ |

根目录保留 AGENTS.md、README.md、ROADMAP.md、.gitignore 和既有 .venv。docs 保留需求、岗位、计划、阶段、学习记录及文章草稿。apps/web 仅放说明，不提前生成 Next.js 项目。不创建空 packages 或构建工具配置。

## 步骤与验收

- 先更新目录规范，记录迁移前代码和图片哈希，再移动文件。
- 更新文档路径、运行命令和图片链接。旧记录中的命令统一到新路径，保留历史结果和日期。
- 根目录命令通过 PYTHONPATH=apps/api 定位包；apps/api 内也可直接调用根目录虚拟环境。测试的 ROOT 仍是 tests 上一级，即 apps/api；练习基于 __file__ 相对加载，保留其实现。
- 验证２４项 unittest、６个练习、预算 7／8 的 CLI 输出、Markdown 本地链接、迁移代码和图片哈希一致、Git 差异检查。
- 更新 ROADMAP 和每日记录，提交后推送 origin/main。

执行结果：２４项 unittest、６个练习全部通过；API 目录 CLI 与根目录预算 7／8 样例通过；１９份迁移文件齐全，代码／依赖／图片哈希一致；Markdown 本地链接有效。测试和练习原有 __file__ 相对路径仍有效，未修改任何 Python 实现。虚拟环境保留，前端仅说明，无新依赖或部署。
