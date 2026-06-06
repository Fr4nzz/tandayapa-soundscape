@echo off
setlocal enabledelayedexpansion
cd /d "d:\Audiomoths"
echo ============================================================
echo   Tandayapa sound-verification server
echo ------------------------------------------------------------
echo   On THIS PC:   http://localhost:8000/outputs/day1/gallery_site/
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
  set ip=%%a
  set ip=!ip: =!
  echo   On the LAN:   http://!ip!:8000/outputs/day1/gallery_site/
)
echo ------------------------------------------------------------
echo   Share a LAN url with others on the same Wi-Fi/network.
echo   If Windows asks, allow Python through the firewall.
echo   Press Ctrl+C in this window to stop the server.
echo ============================================================
start "" "http://localhost:8000/outputs/day1/gallery_site/"
python -m http.server 8000 --bind 0.0.0.0
