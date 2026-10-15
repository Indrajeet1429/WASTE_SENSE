@echo off
cd /d "%~dp0frontend"
if not exist "node_modules" (
  echo Installing frontend packages...
  call npm.cmd install
  if errorlevel 1 pause & exit /b 1
)
call npm.cmd run dev
pause
