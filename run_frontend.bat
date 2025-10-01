@echo off
echo Starting MediBot Frontend Server...
cd /d "c:\Users\Mypc\Desktop\medical_chatbot\frontend\public"
echo Frontend will be available at: http://localhost:8000
python -m http.server 8000
pause