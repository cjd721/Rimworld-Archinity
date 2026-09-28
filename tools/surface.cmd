@echo off
rem Starts the working surface and opens it in the browser. Close this window to stop it.
rem Extra arguments pass through, e.g.: surface.cmd --inventory docs/data/route-inventory.slice.json
cd /d "%~dp0.."
start "" /b cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:8765"
python tools\surface_server.py %*
pause
