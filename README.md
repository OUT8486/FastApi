# 药店管理系统

基于 Vue 3、Element Plus、FastAPI 和 MySQL 8 的前后端分离药店管理系统。新前端位于本项目 `frontend` 目录，原有参考项目不会被修改。

## 功能模块

- 用户登录、退出与注册，登录令牌使用 HMAC-SHA256 签名
- 工作台统计：药品、库存、供应商、客户、采购订单、销售订单和金额
- 药品、客户、供应商、员工、仓库、库存 CRUD
- 采购订单、销售订单和入库记录管理
- 管理员可新增、编辑和删除，普通用户可查看数据
- 自动连接本机 `127.0.0.1:3306` 的 `medicine` 数据库

## 技术栈

- 后端：Python 3.13、FastAPI、PyMySQL、bcrypt
- 前端：Vue 3、Vite、Element Plus、Pinia、Vue Router、Axios
- 数据库：MySQL 8.0 `medicine`

## 目录结构

```text
FastApi/
├─ app/
│  ├─ main.py           FastAPI 应用装配（相当于启动类）
│  ├─ deps.py           依赖注入与认证依赖
│  ├─ core/             配置、密码/JWT、统一响应、业务异常
│  ├─ db/               数据库连接与事务
│  ├─ models/           数据表实体与资源元数据
│  ├─ schemas/          请求 DTO（Pydantic 模型）
│  ├─ dao/              数据访问层（Repository）
│  ├─ services/         业务逻辑层（Service）
│  └─ controllers/      HTTP 控制层（Controller）
├─ frontend/            新的 Vue 3 前端
├─ main.py              后端开发入口
├─ requirements.txt     后端依赖
├─ .env.example         环境变量模板
└─ README.md
```

## 后端分层

后端参照 Spring Boot 的分层方式组织，调用方向固定为
`controller → service → dao → db`，各层职责单一：

- `controllers/` 只处理 HTTP 入参、鉴权依赖与统一响应封装
- `services/` 承载业务规则（必填校验、数值校验、编号生成、异常翻译）
- `dao/` 负责参数化 SQL 与事务，向上返回业务实体，不感知 HTTP
- `db/` 提供连接、事务与查询工具；`core/` 提供配置、加密、响应与异常

接口路径与响应格式保持不变（`{"code": ..., "message": ..., "data": ...}`）。


## 后端启动

首次启动前请复制 `.env.example` 为 `.env`，并将 `JWT_SECRET` 替换为至少 32 字节的随机值；应用会拒绝已知的示例密钥。

```powershell
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```


后端地址：`http://127.0.0.1:8000`  
接口文档：`http://127.0.0.1:8000/docs`  
健康检查：`http://127.0.0.1:8000/health`

## 前端启动

```powershell
cd frontend
npm install
npm run dev
```


前端地址：`http://127.0.0.1:5173`

## 默认测试账号

- 用户名：`admin`
- 密码：`123456`
- 角色：管理员

## 数据库配置

默认配置已经指向本机 `127.0.0.1:3306/medicine`，数据库账号默认为 `root`、密码为 `123456`。如需修改，请调整 `.env` 中的 `DB_HOST`、`DB_PORT`、`DB_USER`、`DB_PASSWORD` 和 `DB_NAME`。

## 验证命令

```powershell
.\.venv\Scripts\python.exe -m compileall -q app main.py
cd frontend
npm run build
```
