#!/usr/bin/env python3
"""
Quick setup script for Secure File Transfer
Run this first to get everything ready
"""

import os
import sys
import secrets
import subprocess

def main():
    print("🔐 Secure File Transfer - Quick Setup")
    print("====================================")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Your version: {sys.version}")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Create directories
    print("\n📁 Creating directories...")
    directories = [
        'uploads', 
        'encrypted_files', 
        'face_encodings', 
        'static/css', 
        'static/js', 
        'static/img'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  ✅ {directory}")
    
    # Create environment file
    print("\n🔧 Creating environment configuration...")
    if not os.path.exists('.env'):
        env_content = f"""SECRET_KEY={secrets.token_hex(32)}
FLASK_ENV=development
FLASK_DEBUG=True
MAX_FILE_SIZE=104857600
ALLOWED_EXTENSIONS=*
FACE_RECOGNITION_TOLERANCE=0.6
FACE_DETECTION_MODEL=hog
TOTP_ISSUER_NAME=Secure File Transfer
TOTP_DIGITS=6
TOTP_INTERVAL=30
"""
        with open('.env', 'w') as f:
            f.write(env_content)
        print("  ✅ .env file created")
    else:
        print("  ✅ .env file already exists")
    
    # Set up virtual environment (optional but recommended)
    print("\n🌐 Setting up Python virtual environment...")
    if not os.path.exists('venv'):
        try:
            subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
            print("  ✅ Virtual environment created")
            
            # Determine activation script path
            if os.name == 'nt':  # Windows
                activate_script = 'venv\\Scripts\\activate'
                pip_path = 'venv\\Scripts\\pip'
            else:  # Unix-like
                activate_script = 'venv/bin/activate'
                pip_path = 'venv/bin/pip'
            
            print(f"  💡 To activate: {activate_script}")
            
        except subprocess.CalledProcessError:
            print("  ⚠️  Could not create virtual environment, continuing...")
    else:
        print("  ✅ Virtual environment already exists")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Install dependencies:")
    print("   pip install -r requirements.txt")
    print("\n2. Start the application:")
    print("   python app.py")
    print("\n3. Open your browser:")
    print("   http://localhost:5000")
    print("\n💡 For production deployment:")
    print("   python manage.py setup")
    print("   ./install.sh")
    print("\n🌍 Perfect for developing countries!")
    print("💰 No cloud costs, complete data control")

if __name__ == '__main__':
    main()
