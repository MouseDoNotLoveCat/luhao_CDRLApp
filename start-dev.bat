@echo off
chcp 65001 >nul
REM 铁路工程质量安全监督问题库管理平台 - 开发启动脚本

echo.
echo ================================================================
echo   铁路工程质量安全监督问题库管理平台 - 开发启动脚本
echo ================================================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未找到 Python
    echo 请先安装 Python 3.10 或更高版本
    pause
    exit /b 1
)

REM 检查 Node.js 是否安装
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未找到 Node.js
    echo 请先安装 Node.js 18.0.0 或更高版本
    pause
    exit /b 1
)

echo [OK] Python 版本:
python --version
echo [OK] Node.js 版本:
node --version
echo [OK] npm 版本:
npm --version
echo.

REM 保存当前目录
set ROOT_DIR=%CD%

REM 启动后端服务
echo [START] 启动后端服务...
echo          后端服务将在 http://localhost:8000 启动
echo.

cd /d "%ROOT_DIR%\backend"
if errorlevel 1 (
    echo [ERROR] 无法进入 backend 目录
    pause
    exit /b 1
)

REM 不使用虚拟环境，直接使用系统 Python (Miniconda)
echo [INSTALL] 检查后端依赖...
pip install -q -r requirements.txt

REM 启动后端服务（后台运行）
start "CDRL Backend" cmd /k "cd /d %ROOT_DIR% && python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000"
echo [OK] Backend service starting...
echo.

REM 等待后端服务启动
timeout /t 3 /nobreak >nul

REM 启动前端开发服务器
echo [START] 启动前端开发服务器...
echo          前端应用将在 http://localhost:3000 启动
echo.

cd /d "%ROOT_DIR%\frontend"
if errorlevel 1 (
    echo [ERROR] 无法进入 frontend 目录
    pause
    exit /b 1
)

REM 检查依赖
if not exist "node_modules" (
    echo [INSTALL] 安装前端依赖...
    call npm install --legacy-peer-deps
)

REM 启动前端开发服务器
start "CDRL Frontend" cmd /k "cd /d %ROOT_DIR%\frontend && npm run dev"

echo.
echo ================================================================
echo   [OK] 应用已启动！
echo ================================================================
echo   后端 API:     http://localhost:8000
echo   后端文档:     http://localhost:8000/docs
echo   前端应用:     http://localhost:3000
echo ================================================================
echo   关闭窗口以停止服务
echo ================================================================
echo.

pause

