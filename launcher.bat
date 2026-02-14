@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"
title Sword Macro Launcher
set "PY=%~dp0.venv\Scripts\python.exe"

rem Last used options (persist across menu returns)
set "last_mode="
set "last_label="
set "last_profile="
set "last_timer_args="
set "last_stop_time="
set "last_sell_args="
set "last_run_type="
set "last_cmd="

:MENU
set "sell_args="
set "profile="
set "timer_args="
cls
echo ==========================================
echo        Sword Macro Launcher
echo ==========================================
echo.
if defined last_cmd (
    echo   [r] Resume last:
    echo       %last_label% / %last_profile%
    if defined last_sell_args echo       Filter: %last_sell_args%
    if defined last_stop_time echo       Timer: %last_stop_time%
    echo       Run: %last_run_type%
    echo.
)
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

if /i "%choice%"=="r" goto RESUME_LAST
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

rem ============================================
rem  [r] Resume with last options
rem ============================================
:RESUME_LAST
if not defined last_cmd (
    echo [!] No previous run found.
    timeout /t 2 >nul
    goto MENU
)
cls
echo ==========================================
echo  Resume last run
echo ==========================================
echo.
echo   Mode:    %last_label%
echo   Profile: %last_profile%
if defined last_sell_args echo   Filter:  %last_sell_args%
if defined last_stop_time echo   Timer:   %last_stop_time% + shutdown
echo   Run:     %last_run_type%
echo.
echo   [1] Start
echo   [0] Back
echo.
set /p rchoice="Select: "
if "%rchoice%"=="0" goto MENU
if "%last_run_type%"=="console" goto RESUME_CONSOLE
if "%last_run_type%"=="background+RDP" goto RESUME_BG_RDP
goto MENU

:RESUME_CONSOLE
cls
echo ==========================================
echo  %last_label% [%last_profile%] - starting in 5s...
echo  Exit: F5 or ESC
echo ==========================================
echo.
%PY% macro.py %last_cmd%
echo.
pause
goto MENU

:RESUME_BG_RDP
cls
echo ==========================================
echo  %last_label% [%last_profile%] - background + RDP
echo ==========================================
echo.
start "" %~dp0.venv\Scripts\pythonw.exe macro.py %last_cmd%
echo [OK] Macro started in background (5s delay).
echo.
echo RDP disconnect in 3 seconds...
timeout /t 3 >nul
call "%~dp0rdp_disconnect.bat"
echo.
pause
goto MENU

rem ============================================
rem  Item filter (shared by all start paths)
rem ============================================
:SELECT_FILTER
cls
echo ==========================================
echo  Item filter
echo ==========================================
echo.
echo   Sell items with specific keywords?
echo   (items with keyword in name = force sell)
echo.
echo   [1] No filter (default)
echo   [2] Sell items containing: sword, club
echo   [3] Custom keywords
echo   [0] Back
echo.
set "sell_args="
set "fchoice="
set /p fchoice="Select: "
if "%fchoice%"=="0" goto MENU
if "%fchoice%"=="2" set "sell_args=--sell-items 검,몽둥이"
if "%fchoice%"=="3" goto CUSTOM_FILTER
goto %filter_return%

:CUSTOM_FILTER
set "sell_kw="
set /p sell_kw="Keywords (comma-separated): "
if not "%sell_kw%"=="" set "sell_args=--sell-items %sell_kw%"
goto %filter_return%

rem ============================================
rem  [1] Start macro (console)
rem ============================================
:START_CONSOLE
set "filter_return=START_CONSOLE_RUN"
goto SELECT_FILTER

:START_CONSOLE_RUN
cls
echo ==========================================
echo  Macro start (console mode)
echo  Exit: F5 or ESC
if not "%sell_args%"=="" echo  Filter: %sell_args%
echo ==========================================
echo.
set "last_mode="
set "last_label=Manual"
set "last_profile=default"
set "last_timer_args="
set "last_stop_time="
set "last_sell_args=%sell_args%"
set "last_run_type=console"
set "last_cmd=%sell_args%"
%PY% macro.py %sell_args%
echo.
pause
goto MENU

rem ============================================
rem  [2] Start macro (background)
rem ============================================
:START_BG
set "filter_return=START_BG_RUN"
goto SELECT_FILTER

:START_BG_RUN
cls
echo ==========================================
echo  Macro start (background)
if not "%sell_args%"=="" echo  Filter: %sell_args%
echo ==========================================
echo.
set "last_mode="
set "last_label=Manual"
set "last_profile=default"
set "last_timer_args="
set "last_stop_time="
set "last_sell_args=%sell_args%"
set "last_run_type=background"
set "last_cmd=%sell_args%"
start "" %~dp0.venv\Scripts\pythonw.exe macro.py %sell_args%
echo [OK] Macro started in background.
echo      Use menu [3] to stop.
echo.
pause
goto MENU

rem ============================================
rem  Auto start flow: [a] Heuristic / [b] AI
rem ============================================
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

:AUTO_TIMER
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

:AUTO_FILTER
set "filter_return=AUTO_RUN_SELECT"
goto SELECT_FILTER

:AUTO_RUN_SELECT
cls
echo ==========================================
echo  %auto_label% [%profile%] - Start
if not "%sell_args%"=="" echo  Filter: %sell_args%
if not "%timer_args%"=="" echo  Timer: %stop_time% + shutdown
echo ==========================================
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

rem Save last options before starting
set "last_mode=%auto_mode%"
set "last_label=%auto_label%"
set "last_profile=%profile%"
set "last_timer_args=%timer_args%"
set "last_stop_time=%stop_time%"
set "last_sell_args=%sell_args%"
set "last_run_type=console"
set "last_cmd=--mode %auto_mode% --delay 5 --profile %profile% %timer_args% %sell_args%"

cls
echo ==========================================
echo  %auto_label% [%profile%] - starting in 5s...
echo  Exit: F5 or ESC
echo ==========================================
echo.
%PY% macro.py --mode %auto_mode% --delay 5 --profile %profile% %timer_args% %sell_args%
set "profile="
set "timer_args="
set "sell_args="
echo.
pause
goto MENU

:AUTO_BG_RDP
rem Save last options before starting
set "last_mode=%auto_mode%"
set "last_label=%auto_label%"
set "last_profile=%profile%"
set "last_timer_args=%timer_args%"
set "last_stop_time=%stop_time%"
set "last_sell_args=%sell_args%"
set "last_run_type=background+RDP"
set "last_cmd=--mode %auto_mode% --delay 5 --profile %profile% %timer_args% %sell_args%"

cls
echo ==========================================
echo  %auto_label% [%profile%] - background + RDP
echo ==========================================
echo.
start "" %~dp0.venv\Scripts\pythonw.exe macro.py --mode %auto_mode% --delay 5 --profile %profile% %timer_args% %sell_args%
set "profile="
set "timer_args="
set "sell_args="
echo [OK] Macro started in background (5s delay).
echo.
echo RDP disconnect in 3 seconds...
timeout /t 3 >nul
call "%~dp0rdp_disconnect.bat"
echo.
pause
goto MENU

rem ============================================
rem  [3] Stop macro
rem ============================================
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

rem ============================================
rem  Tools
rem ============================================
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
