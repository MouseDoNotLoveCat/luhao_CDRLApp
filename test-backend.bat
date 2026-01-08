@echo off
chcp 65001 >nul
echo ================================================================
echo   测试后端启动
echo ================================================================
echo.

cd backend
echo 当前目录: %CD%
echo.

echo 检查 main.py 是否存在...
if exist "app\main.py" (
    echo [OK] app\main.py 存在
) else (
    echo [ERROR] app\main.py 不存在
    pause
    exit /b 1
)
echo.

echo 检查数据库是否存在...
if exist "cdrl.db" (
    echo [OK] cdrl.db 存在
) else (
    echo [WARNING] cdrl.db 不存在
)
echo.

echo 尝试启动后端服务...
echo 命令: python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo.
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause

