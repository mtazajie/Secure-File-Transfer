@echo off
echo 🔐 Secure File Transfer - Windows Setup
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found
python --version

echo.
echo 📁 Creating directories...
if not exist "uploads" mkdir uploads
if not exist "encrypted_files" mkdir encrypted_files
if not exist "face_encodings" mkdir face_encodings
if not exist "static\css" mkdir static\css
if not exist "static\js" mkdir static\js
if not exist "static\img" mkdir static\img
echo ✅ Directories created

echo.
echo 🌐 Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

echo.
echo 📦 Activating virtual environment and installing packages...
call venv\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing basic requirements (without face recognition)...
pip install -r requirements-basic.txt

echo.
echo 🔧 Creating environment file...
if not exist ".env" (
    echo SECRET_KEY=your-secret-key-change-this-in-production > .env
    echo FLASK_ENV=development >> .env
    echo FLASK_DEBUG=True >> .env
    echo MAX_FILE_SIZE=104857600 >> .env
    echo ALLOWED_EXTENSIONS=* >> .env
    echo FACE_RECOGNITION_TOLERANCE=0.6 >> .env
    echo FACE_DETECTION_MODEL=hog >> .env
    echo TOTP_ISSUER_NAME=Secure File Transfer >> .env
    echo TOTP_DIGITS=6 >> .env
    echo TOTP_INTERVAL=30 >> .env
    echo ✅ Environment file created
) else (
    echo ✅ Environment file already exists
)

echo.
echo 🎉 Basic setup completed!
echo.
echo 📋 Next steps:
echo 1. To start the application:
echo    venv\Scripts\activate.bat
echo    python app.py
echo.
echo 2. Open browser to: http://localhost:5000
echo.
echo 💡 Optional: Install face recognition
echo    For face recognition features, you need Visual Studio Build Tools
echo    Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
echo    Then run: pip install face-recognition opencv-python
echo.
echo 🌍 Perfect for developing countries - no cloud costs!
echo.
pause
