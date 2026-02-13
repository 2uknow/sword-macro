@echo off
REM 검 강화 매크로를 백그라운드에서 실행
echo ======================================
echo 검 강화 매크로 백그라운드 실행
echo ======================================
echo.
echo 매크로가 백그라운드에서 실행됩니다.
echo 종료하려면 작업 관리자에서 pythonw.exe를 종료하세요.
echo.

REM pythonw.exe로 콘솔 없이 실행
start "" pythonw.exe macro.py

echo 매크로가 시작되었습니다!
echo 이 창을 닫아도 매크로는 계속 실행됩니다.
echo.
pause
