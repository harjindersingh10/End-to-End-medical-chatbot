@echo off
echo Starting Medical Chatbot Application...

echo.
echo Installing backend dependencies...
cd backend
pip install -r requirements.txt

echo.
echo Starting Flask backend...
start cmd /k "python app.py"

echo.
echo Installing frontend dependencies...
cd ../frontend
call npm install

echo.
echo Starting React frontend...
start cmd /k "npm start"

echo.
echo Application started!
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
pause