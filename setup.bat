@echo off
REM PDF Processing Application - Quick Start Script for Windows
REM This script sets up and runs both backend and frontend

setlocal enabledelayedexpansion

echo 🚀 PDF Processing Application - Quick Start
echo ===========================================

REM Check prerequisites
echo.
echo 📋 Checking prerequisites...

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.9+
    exit /b 1
)

where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js 16+
    exit /b 1
)

where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ npm is not installed. Please install npm
    exit /b 1
)

echo ✅ All prerequisites found

REM Setup Backend
echo.
echo 🔧 Setting up backend...

cd backend

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install -q -r requirements.txt

echo ✅ Backend setup complete

REM Setup Frontend
echo.
echo 🎨 Setting up frontend...

cd ..\frontend

if not exist "node_modules" (
    echo Installing Node.js dependencies...
    call npm install
) else (
    echo Dependencies already installed
)

echo ✅ Frontend setup complete

echo.
echo ===========================================
echo ✅ Setup complete!
echo.
echo 📝 To run the application:
echo.
echo Terminal 1 (Backend):
echo   cd backend
echo   venv\Scripts\activate.bat
echo   python -m uvicorn app.main:app --reload --port 8000
echo.
echo Terminal 2 (Frontend):
echo   cd frontend
echo   npm run dev
echo.
echo Then open: http://localhost:5173
echo.
echo 🚀 Happy coding!
