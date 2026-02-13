@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"
title Sword Macro Launcher
set "PY=%~dp0.venv\Scripts\python.exe"

:MENU
cls
echo ==========================================
echo        Sword Macro Launcher
echo ==========================================
echo.
echo   --- Macro ---
echo   [1] Start macro (console)
echo   [2] Start macro (background)
echo   [3] Stop macro
echo.
echo   --- Auto start (5s delay) ---
echo   [a] Heuristic auto (F4) + profile select
echo   [b] AI auto (F3) + profile select
echo.
echo   --- Tools ---
echo   [4] Get coordinates (pyautogui)
echo   [5] Check screen info
echo   [6] Test coordinates
echo   [7] Train AI model
echo   [8] TensorBoard
echo   [9] Open config (notepad)
echo.
echo   --- Remote Desktop ---
echo   [d] RDP safe disconnect (keep session)
echo.
echo   [0] Exit
echo.
echo ==========================================
set /p choice="Select: "

if "%choice%"=="1" goto START_CONSOLE
if "%choice%"=="2" goto START_BG
if "%choice%"=="3" goto STOP
if "%choice%"=="4" goto COORDS
if "%choice%"=="5" goto SCREEN_INFO
if "%choice%"=="6" goto TEST_COORDS
if "%choice%"=="7" goto TRAIN
if "%choice%"=="8" goto TENSORBOARD
if "%choice%"=="9" goto CONFIG
if "%choice%"=="0" goto EXIT
if /i "%choice%"=="a" goto AUTO_HEURISTIC
if /i "%choice%"=="b" goto AUTO_AI
if /i "%choice%"=="d" goto RDP_DISCONNECT

echo.
echo [!] Invalid input.
timeout /t 2 >nul
goto MENU

:AUTO_HEURISTIC
set "auto_mode=heuristic"
set "auto_label=Heuristic"
goto SELECT_PROFILE

:AUTO_AI
set "auto_mode=ai"
set "auto_label=AI"
goto SELECT_PROFILE

:SELECT_PROFILE
cls
echo ==========================================
echo  %auto_label% auto mode - Select profile
echo ==========================================
echo.
echo   [1] Home
echo   [2] Work (RDP)
echo   [3] Work_local (physical monitor)
echo   [0] Back
echo.
set /p pchoice="Select: "
if "%pchoice%"=="1" set "profile=home"
if "%pchoice%"=="2" set "profile=work"
if "%pchoice%"=="3" set "profile=work_local"
if "%pchoice%"=="0" goto MENU
if not defined profile goto MENU
cls
echo ==========================================
echo  %auto_label% [%profile%] - Timer setting
echo ==========================================
echo.
echo   Stop time? (HH:MM format, e.g. 18:00)
echo   Press Enter to skip (run forever)
echo.
set "stop_time="
set /p stop_time="Stop at: "
set "timer_args="
if not "%stop_time%"=="" (
    set "timer_args=--until %stop_time% --shutdown"
    echo.
    echo   >> Will stop at %stop_time% + PC shutdown
)
echo.
echo   [1] Console (foreground)
echo   [2] Background + RDP disconnect
echo   [0] Back
echo.
set /p rchoice="Select: "
if "%rchoice%"=="0" (
    set "profile="
    goto MENU
)
if "%rchoice%"=="2" goto AUTO_BG_RDP
cls
echo ==========================================
echo  %auto_label% [%profile%] - starting in 5s...
echo  Exit: F5 or ESC
echo ==========================================
echo.
%PY% macro.py --mode %auto_mode% --delay 5 --profile %profile% %timer_args%
set "profile="
set "timer_args="
echo.
pause
goto MENU

:AUTO_BG_RDP
cls
echo ==========================================
echo  %auto_label% [%profile%] - background + RDP
echo ==========================================
echo.
start "" %~dp0.venv\Scripts\pythonw.exe macro.py --mode %auto_mode% --delay 5 --profile %profile% %timer_args%
set "profile="
set "timer_args="
echo [OK] Macro started in background (5s delay).
echo.
echo RDP disconnect in 3 seconds...
echo (UAC prompt will appear if not admin)
timeout /t 3 >nul
call "%~dp0rdp_disconnect.bat"
echo.
pause
goto MENU

:START_CONSOLE
cls
echo ==========================================
echo  Macro start (console mode)
echo  Exit: F5 or ESC
echo ==========================================
echo.
%PY% macro.py
echo.
pause
goto MENU

:START_BG
cls
echo ==========================================
echo  Macro start (background)
echo ==========================================
echo.
start "" %~dp0.venv\Scripts\pythonw.exe macro.py
echo [OK] Macro started in background.
echo      Use menu [3] to stop.
echo.
pause
goto MENU

:STOP
cls
echo ==========================================
echo  Stop macro
echo ==========================================
echo.
taskkill /F /IM pythonw.exe 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Macro stopped.
) else (
    echo [!] No background macro found.
)
echo.
pause
goto MENU

:COORDS
cls
echo ==========================================
echo  Get coordinates (pyautogui)
echo  Ctrl+C to exit
echo ==========================================
echo.
%PY% get_coordinates_pyautogui.py
echo.
pause
goto MENU

:SCREEN_INFO
cls
echo ==========================================
echo  Screen info
echo ==========================================
echo.
%PY% check_screen_info.py
echo.
pause
goto MENU

:TEST_COORDS
cls
echo ==========================================
echo  Test coordinates
echo ==========================================
echo.
%PY% test_coordinates.py
echo.
pause
goto MENU

:TRAIN
cls
echo ==========================================
echo  Train AI model
echo ==========================================
echo.
echo   [1] Default (1,000,000 steps)
echo   [2] Long (5,000,000 steps)
echo   [3] Extra long (10,000,000 steps)
echo   [0] Back
echo.
set /p tchoice="Select: "
if "%tchoice%"=="1" (
    %PY% -m rl.train
) else if "%tchoice%"=="2" (
    %PY% -m rl.train -t 5000000
) else if "%tchoice%"=="3" (
    %PY% -m rl.train -t 10000000
) else (
    goto MENU
)
echo.
pause
goto MENU

:TENSORBOARD
cls
echo ==========================================
echo  TensorBoard
echo  Open http://localhost:6006 in browser
echo  Ctrl+C to exit
echo ==========================================
echo.
start http://localhost:6006
%~dp0.venv\Scripts\tensorboard.exe --logdir ./logs/
echo.
pause
goto MENU

:CONFIG
cls
echo ==========================================
echo  Open config
echo ==========================================
echo.
start notepad rl\config.py
echo [OK] config.py opened in notepad.
echo.
pause
goto MENU

:RDP_DISCONNECT
cls
echo ==========================================
echo  RDP safe disconnect
echo ==========================================
echo.
echo  Disconnect RDP but keep desktop session
echo  alive so the macro keeps running.
echo  (UAC prompt will appear if not admin)
echo.
echo   [1] Disconnect (keep session)
echo   [0] Back
echo.
set /p dchoice="Select: "
if "%dchoice%"=="1" (
    call "%~dp0rdp_disconnect.bat"
) else (
    goto MENU
)
echo.
pause
goto MENU

:EXIT
cls
echo Bye!
timeout /t 1 >nul
exit /b 0
