@echo off
title 校园售货机控制台
color 0a

echo ==========================================
echo      正在启动校园售货机系统...
echo ==========================================

:: 1. 启动 Redis (后台运行)
:: 【请修改】下面这行改成你 Redis 的真实路径
start "Redis Server" /min ""D:\Redis-x64-5.0.14.1\redis-server.exe""

:: 等待 2 秒让 Redis 跑起来
timeout /t 2 /nobreak >nul

:: 2. 启动 Python 后端
echo 正在启动后端服务...
:: 这里假设你用的是项目里的虚拟环境 .venv
:: 如果没用虚拟环境，直接写 uvicorn app.main:app --reload
start "Python Backend" cmd /k "call .venv\Scripts\activate && uvicorn app.main:app --reload"

:: 等待 3 秒让后端跑起来
timeout /t 3 /nobreak >nul

:: 3. 自动打开浏览器
echo 正在打开网页...
start http://127.0.0.1:8000

echo.
echo ==========================================
echo      系统启动成功！请在网页操作。
echo      关闭此窗口将退出系统。
echo ==========================================
pause