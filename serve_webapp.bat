@echo off
setlocal enabledelayedexpansion
cd /d "d:\Audiomoths"
echo ============================================================
echo   Tandayapa Soundscape  (React web app)
echo ------------------------------------------------------------
echo   On THIS PC:   http://localhost:8000/webapp/dist/
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
  set ip=%%a
  set ip=!ip: =!
  echo   On the LAN:   http://!ip!:8000/webapp/dist/
)
echo ------------------------------------------------------------
echo   Share a LAN url with others on the same network.
echo   Audio + data stream from this PC. Allow Python through the
echo   firewall if asked. Press Ctrl+C to stop.
echo ------------------------------------------------------------
echo   To refresh after new detections:
echo     Rscript export_web_data.R   then reload the page.
echo   To rebuild the app after code changes:
echo     cd webapp ^&^& npm run build
echo ============================================================
start "" "http://localhost:8000/webapp/dist/"
python -m http.server 8000 --bind 0.0.0.0
