@echo off
REM 快速修复脚本 - 解决常见问题

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║  CDRL 项目 - 快速修复脚本                                     ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

:menu
echo 请选择要执行的操作:
echo.
echo 1. 清除所有缓存并重新安装依赖
echo 2. 只清除后端缓存
echo 3. 只清除前端缓存
echo 4. 检查 Node.js 版本
echo 5. 检查 Python 版本
echo 6. 查看后端日志
echo 7. 杀死所有 Node.js 进程
echo 8. 杀死所有 Python 进程
echo 9. 重置整个项目
echo 0. 退出
echo.
set /p choice="请输入选项 (0-9): "

if "%choice%"=="1" goto clean_all
if "%choice%"=="2" goto clean_backend
if "%choice%"=="3" goto clean_frontend
if "%choice%"=="4" goto check_node
if "%choice%"=="5" goto check_python
if "%choice%"=="6" goto view_log
if "%choice%"=="7" goto kill_node
if "%choice%"=="8" goto kill_python
if "%choice%"=="9" goto reset_project
if "%choice%"=="0" goto end
echo 无效的选项
echo.
goto menu

:clean_all
echo.
echo 🧹 清除所有缓存...
echo 清除后端缓存...
cd backend
if exist venv rmdir /s /q venv
if exist __pycache__ rmdir /s /q __pycache__
if exist .pytest_cache rmdir /s /q .pytest_cache
cd ..

echo 清除前端缓存...
cd frontend
if exist node_modules rmdir /s /q node_modules
if exist package-lock.json del package-lock.json
if exist dist rmdir /s /q dist
if exist .vite rmdir /s /q .vite
cd ..

echo ✅ 缓存清除完成
echo.
goto menu

:clean_backend
echo.
echo 🧹 清除后端缓存...
cd backend
if exist venv rmdir /s /q venv
if exist __pycache__ rmdir /s /q __pycache__
if exist .pytest_cache rmdir /s /q .pytest_cache
cd ..
echo ✅ 后端缓存清除完成
echo.
goto menu

:clean_frontend
echo.
echo 🧹 清除前端缓存...
cd frontend
if exist node_modules rmdir /s /q node_modules
if exist package-lock.json del package-lock.json
if exist dist rmdir /s /q dist
if exist .vite rmdir /s /q .vite
cd ..
echo ✅ 前端缓存清除完成
echo.
goto menu

:check_node
echo.
echo 📦 检查 Node.js 版本...
node --version
if errorlevel 1 (
    echo ❌ 未找到 Node.js
) else (
    echo ✅ Node.js 已安装
)
echo.
goto menu

:check_python
echo.
echo 📦 检查 Python 版本...
python --version
if errorlevel 1 (
    echo ❌ 未找到 Python
) else (
    echo ✅ Python 已安装
)
echo.
goto menu

:view_log
echo.
echo 📋 后端日志:
if exist "%TEMP%\backend.log" (
    type "%TEMP%\backend.log"
) else (
    echo 未找到后端日志文件
)
echo.
goto menu

:kill_node
echo.
echo ⚠️  杀死所有 Node.js 进程...
taskkill /F /IM node.exe 2>nul
taskkill /F /IM npm.cmd 2>nul
echo ✅ 完成
echo.
goto menu

:kill_python
echo.
echo ⚠️  杀死所有 Python 进程...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul
echo ✅ 完成
echo.
goto menu

:reset_project
echo.
echo ⚠️  警告: 这将删除所有缓存和依赖
set /p confirm="确定要继续吗? (y/n): "

if /i "%confirm%"=="y" (
    echo.
    echo 🔄 重置项目...
    
    REM 杀死所有进程
    taskkill /F /IM node.exe 2>nul
    taskkill /F /IM npm.cmd 2>nul
    taskkill /F /IM python.exe 2>nul
    taskkill /F /IM pythonw.exe 2>nul
    
    REM 清除所有缓存
    echo 清除后端缓存...
    cd backend
    if exist venv rmdir /s /q venv
    if exist __pycache__ rmdir /s /q __pycache__
    cd ..
    
    echo 清除前端缓存...
    cd frontend
    if exist node_modules rmdir /s /q node_modules
    if exist package-lock.json del package-lock.json
    cd ..
    
    echo ✅ 项目重置完成
    echo 现在可以运行: start-dev.bat
) else (
    echo 已取消
)
echo.
goto menu

:end
echo 退出
endlocal

