@echo off
echo Adding Windows Firewall rule for Python Backend on port 8000...
netsh advfirewall firewall add rule name="Python Backend HTTP" dir=in action=allow protocol=TCP localport=8000
echo.
echo Firewall rule added successfully!
echo.
echo Now test from other device:
echo 1. Go to: http://192.168.0.53:8000/health
echo 2. Should see: {"status":"healthy"...}
echo.
pause