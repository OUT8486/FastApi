@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

rem 用法: start.bat [backend^|frontend^|all]   默认 all

if /i "%~1"=="backend"  goto backend
if /i "%~1"=="frontend" goto frontend
if /i "%~1"=="all"      goto all
if not "%~1"=="" (
    echo 用法: start.bat [backend^|frontend^|all]
    exit /b 1
)

:all
echo 正在启动后端和前端...
start "药店管理系统 - 后端" cmd /k ""%~f0" backend"
start "药店管理系统 - 前端" cmd /k ""%~f0" frontend"
echo.
echo 后端: http://127.0.0.1:8000/docs
echo 前端: http://127.0.0.1:5173
echo 两个服务分别在独立窗口运行，关闭对应窗口即可停止。
timeout /t 3 >nul
exit /b 0

:backend
echo === 后端启动 ^(FastAPI^) ===

if not exist ".env" (
    if exist ".env.example" (
        copy /y ".env.example" ".env" >nul
        echo 已根据 .env.example 生成 .env，请确认数据库账号密码和 JWT_SECRET。
    ) else (
        echo 缺少 .env 文件，请先配置数据库连接信息。
        exit /b 1
    )
)

set "PYTHON=.venv\Scripts\python.exe"
if not exist "%PYTHON%" set "PYTHON=python"

"%PYTHON%" -c "import fastapi, uvicorn, pymysql, bcrypt" >nul 2>&1
if errorlevel 1 (
    echo 正在安装后端依赖...
    "%PYTHON%" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo 后端依赖安装失败。
        exit /b 1
    )
)

echo 后端地址: http://127.0.0.1:8000
echo 接口文档: http://127.0.0.1:8000/docs
echo 按 Ctrl+C 停止服务。
echo.
"%PYTHON%" main.py
exit /b %errorlevel%

:frontend
cd /d "%~dp0frontend"
echo === 前端启动 ^(Vue 3 + Vite^) ===

where npm >nul 2>&1
if errorlevel 1 (
    echo 未找到 npm，请先安装 Node.js: https://nodejs.org
    exit /b 1
)

if not exist "node_modules" (
    echo 正在安装前端依赖 ^(npm install^)...
    call npm install
    if errorlevel 1 (
        echo 前端依赖安装失败。
        exit /b 1
    )
)

echo 前端地址: http://127.0.0.1:5173
echo 接口请求会通过 /api 代理到后端 http://127.0.0.1:8000
echo 按 Ctrl+C 停止服务。
echo.
call npm run dev
exit /b %errorlevel%