#!/usr/bin/env python3
"""
Secure File Transfer - Management Script
For use in developing countries where cloud services are expensive
"""

import argparse
import os
import sys
import subprocess
import psutil
import json
from datetime import datetime

def check_system_requirements():
    """Check if system meets minimum requirements"""
    print("🔍 Checking system requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    print("✅ Python version OK")
    
    # Check memory
    memory = psutil.virtual_memory()
    if memory.total < 1024 * 1024 * 1024:  # 1GB
        print("⚠️  Warning: Less than 1GB RAM available")
    else:
        print("✅ Memory OK")
    
    # Check disk space
    disk = psutil.disk_usage('.')
    if disk.free < 5 * 1024 * 1024 * 1024:  # 5GB
        print("⚠️  Warning: Less than 5GB disk space available")
    else:
        print("✅ Disk space OK")
    
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    directories = ['uploads', 'encrypted_files', 'face_encodings', 'static/css', 'static/js']
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created {directory}")

def setup_environment():
    """Setup environment file"""
    print("🔧 Setting up environment...")
    
    if not os.path.exists('.env'):
        import secrets
        env_content = f"""SECRET_KEY={secrets.token_hex(32)}
FLASK_ENV=production
FLASK_DEBUG=False
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
        print("✅ Environment file created")
    else:
        print("✅ Environment file exists")

def check_service_status():
    """Check if the service is running"""
    try:
        result = subprocess.run(['systemctl', 'is-active', 'secure-file-transfer'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Service is running")
            return True
        else:
            print("❌ Service is not running")
            return False
    except FileNotFoundError:
        print("ℹ️  systemctl not available (not running on systemd)")
        return None

def start_development_server():
    """Start development server"""
    print("🚀 Starting development server...")
    print("📡 Server will be available at: http://localhost:5000")
    print("🔒 Use Ctrl+C to stop the server")
    
    try:
        subprocess.run([sys.executable, 'app.py'])
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

def show_system_info():
    """Show system information"""
    print("\n💻 System Information:")
    print(f"OS: {os.name}")
    print(f"Python: {sys.version.split()[0]}")
    
    # Memory
    memory = psutil.virtual_memory()
    print(f"Memory: {memory.total // (1024**3)}GB total, {memory.available // (1024**3)}GB available")
    
    # Disk
    disk = psutil.disk_usage('.')
    print(f"Disk: {disk.total // (1024**3)}GB total, {disk.free // (1024**3)}GB free")
    
    # CPU
    print(f"CPU: {psutil.cpu_count()} cores")

def backup_data():
    """Create backup of encrypted files and user data"""
    print("💾 Creating backup...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backup_{timestamp}"
    
    os.makedirs(backup_dir, exist_ok=True)
    
    # Copy encrypted files
    if os.path.exists('encrypted_files'):
        subprocess.run(['cp', '-r', 'encrypted_files', backup_dir])
        print(f"✅ Encrypted files backed up to {backup_dir}")
    
    # Copy face encodings
    if os.path.exists('face_encodings'):
        subprocess.run(['cp', '-r', 'face_encodings', backup_dir])
        print(f"✅ Face encodings backed up to {backup_dir}")
    
    print(f"📦 Backup completed: {backup_dir}")

def show_logs():
    """Show application logs"""
    print("📋 Recent logs:")
    
    # Try to show systemd logs first
    try:
        subprocess.run(['journalctl', '-u', 'secure-file-transfer', '-n', '20', '--no-pager'])
    except FileNotFoundError:
        # Fallback to app logs if available
        if os.path.exists('app.log'):
            subprocess.run(['tail', '-20', 'app.log'])
        else:
            print("No logs found")

def show_stats():
    """Show usage statistics"""
    print("📊 Usage Statistics:")
    
    # Count encrypted files
    encrypted_count = 0
    if os.path.exists('encrypted_files'):
        encrypted_count = len([f for f in os.listdir('encrypted_files') if f.endswith('.enc')])
    
    # Count users (face encodings)
    user_count = 0
    if os.path.exists('face_encodings'):
        user_count = len([f for f in os.listdir('face_encodings') if f.endswith('.npy')])
    
    print(f"👥 Users: {user_count}")
    print(f"📁 Encrypted files: {encrypted_count}")
    
    # Calculate total storage used
    total_size = 0
    for root, dirs, files in os.walk('.'):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.exists(file_path):
                total_size += os.path.getsize(file_path)
    
    print(f"💾 Storage used: {total_size // (1024**2)}MB")

def main():
    parser = argparse.ArgumentParser(description='Secure File Transfer Management')
    parser.add_argument('command', choices=[
        'setup', 'start', 'status', 'info', 'backup', 'logs', 'stats', 'check'
    ], help='Command to execute')
    
    if len(sys.argv) == 1:
        # No arguments provided, show help
        print("🔐 Secure File Transfer - Management Tool")
        print("========================================")
        print("\nAvailable commands:")
        print("  setup  - Setup the application")
        print("  start  - Start development server")
        print("  status - Check service status")
        print("  info   - Show system information")
        print("  backup - Create data backup")
        print("  logs   - Show recent logs")
        print("  stats  - Show usage statistics")
        print("  check  - Check system requirements")
        print("\nExample: python manage.py setup")
        return
    
    args = parser.parse_args()
    
    if args.command == 'setup':
        print("🔐 Setting up Secure File Transfer...")
        if check_system_requirements():
            create_directories()
            setup_environment()
            install_dependencies()
            print("\n✅ Setup completed successfully!")
            print("💡 Next steps:")
            print("   python manage.py start  # Start development server")
            print("   python manage.py status # Check status")
    
    elif args.command == 'start':
        start_development_server()
    
    elif args.command == 'status':
        check_service_status()
        show_stats()
    
    elif args.command == 'info':
        show_system_info()
    
    elif args.command == 'backup':
        backup_data()
    
    elif args.command == 'logs':
        show_logs()
    
    elif args.command == 'stats':
        show_stats()
    
    elif args.command == 'check':
        check_system_requirements()

if __name__ == '__main__':
    main()
