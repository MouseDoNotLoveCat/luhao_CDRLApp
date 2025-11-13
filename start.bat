@echo off
REM CDRLApp 启动脚本 (Windows)
REM 用法: start.bat

setlocal enabledelayedexpansion

REM 颜色定义
set "BLUE=[94m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "NC=[0m"

echo.
echo ╔════════════════════════════════════════╗
echo ║   CDRLApp - 启动程序                   ║
echo ║   Railway Construction Quality         ║
echo ║   Supervision Issue Database           ║
echo ╚════════════════════════════════════════╝
echo.

REM 检查环境
echo [94mℹ️  检查环境...%NC%

where node >nul 2>nul
if errorlevel 1 (
    echo [91m❌ Node.js 未安装%NC%
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo [92m✅ Node.js 已安装: %NODE_VERSION%%NC%

where python >nul 2>nul
if errorlevel 1 (
    echo [91m❌ Python 未安装%NC%
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [92m✅ Python 已安装: %PYTHON_VERSION%%NC%

where npm >nul 2>nul
if errorlevel 1 (
    echo [91m❌ npm 未安装%NC%
    exit /b 1
)
for /f "tokens=*" %%i in ('npm --version') do set NPM_VERSION=%%i
echo [92m✅ npm 已安装: %NPM_VERSION%%NC%

echo.

REM 启动后端
echo [94mℹ️  启动后端服务...%NC%

cd backend

if not exist "venv" (
    echo [93m⚠️  虚拟环境不存在，创建虚拟环境...%NC%
    python -m venv venv
)

call venv\Scripts\activate.bat

if exist "requirements.txt" (
    pip install -q -r requirements.txt
)

echo [92m✅ 后端服务启动中...%NC%
start "CDRLApp Backend" python -m uvicorn app.main:app --reload --port 8000

cd ..

timeout /t 2 /nobreak

echo [92m✅ 后端服务已启动%NC%
echo [94mℹ️  后端地址: http://localhost:8000%NC%

echo.

REM 启动前端
echo [94mℹ️  启动前端服务...%NC%

cd frontend

if not exist "node_modules" (
    echo [93m⚠️  node_modules 不存在，安装依赖...%NC%
    call npm install
)

echo [92m✅ 前端服务启动中...%NC%
start "CDRLApp Frontend" npm run dev

cd ..

timeout /t 3 /nobreak

echo [92m✅ 前端服务已启动%NC%
echo [94mℹ️  前端地址: http://localhost:3001%NC%

echo.

echo ═══════════════════════════════════════
echo [92m✅ 所有服务已启动%NC%
echo ═══════════════════════════════════════
echo.
echo 📱 前端应用: http://localhost:3001
echo 🔌 后端 API: http://localhost:8000
echo 📚 API 文档: http://localhost:8000/docs
echo.
echo [93m按 Ctrl+C 停止服务%NC%
echo.

pause

