@echo off
REM 백그라운드에서 실행 중인 매크로 종료
echo ======================================
echo 검 강화 매크로 종료
echo ======================================
echo.

REM pythonw.exe 프로세스 중 macro.py를 실행 중인 것 찾아서 종료
taskkill /F /FI "IMAGENAME eq pythonw.exe" /FI "WINDOWTITLE eq macro.py*" 2>nul

if %ERRORLEVEL% EQU 0 (
    echo 매크로가 종료되었습니다!
) else (
    echo 실행 중인 매크로를 찾을 수 없습니다.
    echo 작업 관리자에서 pythonw.exe 프로세스를 직접 종료하세요.
)

echo.
pause
