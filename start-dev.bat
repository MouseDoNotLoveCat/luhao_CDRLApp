@echo off
REM 铁路工程质量安全监督问题库管理平台 - 开发启动脚本

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║  铁路工程质量安全监督问题库管理平台 - 开发启动脚本            ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Python
    echo 请先安装 Python 3.8 或更高版本
    pause
    exit /b 1
)

REM 检查 Node.js 是否安装
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Node.js
    echo 请先安装 Node.js 18.0.0 或更高版本
    pause
    exit /b 1
)

echo ✅ Python 版本:
python --version
echo ✅ Node.js 版本:
node --version
echo ✅ npm 版本:
npm --version
echo.

REM 启动后端服务
echo 🚀 启动后端服务...
echo    后端服务将在 http://localhost:8000 启动
echo.

cd backend

REM 检查虚拟环境
if not exist "venv" (
    echo 📦 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 安装依赖
echo 📦 安装后端依赖...
pip install -q -r requirements.txt

REM 启动后端服务（后台运行）
start "CDRL Backend" python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo ✅ 后端服务已启动
echo.

REM 等待后端服务启动
timeout /t 3 /nobreak

REM 启动前端开发服务器
echo 🚀 启动前端开发服务器...
echo    前端应用将在 http://localhost:3000 启动
echo.

cd ..\frontend

REM 检查依赖
if not exist "node_modules" (
    echo 📦 安装前端依赖...
    call npm install
)

REM 启动前端开发服务器
start "CDRL Frontend" cmd /k npm run dev

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║  ✅ 应用已启动！                                              ║
echo ╠════════════════════════════════════════════════════════════════╣
echo ║  后端 API:     http://localhost:8000                          ║
echo ║  后端文档:     http://localhost:8000/docs                     ║
echo ║  前端应用:     http://localhost:3000                          ║
echo ╠════════════════════════════════════════════════════════════════╣
echo ║  关闭窗口以停止服务                                            ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

pause

