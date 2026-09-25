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
├─ app/                 FastAPI 应用、配置、数据库、认证与路由
├─ frontend/            新的 Vue 3 前端
├─ main.py              后端开发入口
├─ requirements.txt     后端依赖
├─ .env.example         环境变量模板
└─ README.md
```


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

