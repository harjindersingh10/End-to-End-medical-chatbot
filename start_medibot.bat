@echo off
echo ========================================
echo    Starting ClinixAI Medical Chatbot
echo ========================================
echo.
echo [1] Starting Backend Server...
start "MediBot Backend" cmd /k "cd /d c:\Users\Mypc\Desktop\medical_chatbot\backend && python simple_app.py"

timeout /t 3 /nobreak >nul

echo [2] Starting Frontend Server...
start "MediBot Frontend" cmd /k "cd /d c:\Users\Mypc\Desktop\medical_chatbot\frontend\public && python -m http.server 8000"

timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo   ClinixAI Medical Chatbot Started!
echo ========================================
echo.
echo Backend API: http://localhost:5000
echo Frontend UI: http://localhost:8000
echo.
echo Open your browser and go to: http://localhost:8000
echo.
echo Press any key to close this window...
pause >nul