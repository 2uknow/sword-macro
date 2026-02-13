@echo off
echo ==========================================
echo  RDP Disconnect (tsdiscon)
echo ==========================================
echo.

for /f "tokens=3" %%a in ('query session %USERNAME% ^| findstr /i "%USERNAME%"') do set SID=%%a

if not defined SID (
    echo [!] No session found.
    pause
    exit /b 1
)

echo Session ID: %SID%
echo Disconnecting RDP session...
echo.
tsdiscon %SID%
if %ERRORLEVEL% EQU 0 (
    echo [OK] RDP session disconnected.
) else (
    echo [!] Failed to disconnect. Exit code: %ERRORLEVEL%
)

pause
