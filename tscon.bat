@echo off
:: 관리자 권한으로 실행 필요
for /f "tokens=3" %%a in ('query session %USERNAME% ^| findstr /i "%USERNAME%"') do set SID=%%a
tscon %SID% /dest:console/강화

