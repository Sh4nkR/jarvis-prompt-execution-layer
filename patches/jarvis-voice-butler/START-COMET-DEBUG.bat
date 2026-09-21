@echo off
setlocal
set PORT=9222
set EXE=

if exist "%LOCALAPPDATA%\Perplexity\Comet\Application\comet.exe" set EXE=%LOCALAPPDATA%\Perplexity\Comet\Application\comet.exe
if exist "%LOCALAPPDATA%\Comet\Application\comet.exe" set EXE=%LOCALAPPDATA%\Comet\Application\comet.exe
if exist "%PROGRAMFILES%\Perplexity\Comet\Application\comet.exe" set EXE=%PROGRAMFILES%\Perplexity\Comet\Application\comet.exe
if exist "%PROGRAMFILES%\Comet\Application\comet.exe" set EXE=%PROGRAMFILES%\Comet\Application\comet.exe

if "%EXE%"=="" (
  echo Comet not found. Run FIND-COMET.bat and tell me the path.
  pause
  exit /b 1
)

echo Using %EXE%
echo Close other Comet windows if this fails to attach.
start "" "%EXE%" --remote-debugging-port=%PORT% --remote-debugging-address=127.0.0.1
timeout /t 3 /nobreak >nul
curl -s http://127.0.0.1:9222/json/version
echo.
echo If you saw JSON above, Comet is ready for Jarvis.
pause
