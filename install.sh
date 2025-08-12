#!/bin/bash

# Secure File Transfer - Installation Script for Developing Countries
# This script sets up the secure file transfer system on Ubuntu/Debian systems

echo "🔐 Secure File Transfer - Installation Script"
echo "==============================================="

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and pip
echo "🐍 Installing Python and pip..."
sudo apt install python3 python3-pip python3-venv -y

# Install system dependencies for face recognition
echo "📷 Installing face recognition dependencies..."
sudo apt install build-essential cmake libopenblas-dev liblapack-dev -y
sudo apt install libx11-dev libgtk-3-dev -y
sudo apt install python3-dev -y

# Install OpenCV dependencies
echo "🎥 Installing OpenCV dependencies..."
sudo apt install libopencv-dev python3-opencv -y

# Install additional libraries for cryptography
echo "🔒 Installing cryptography dependencies..."
sudo apt install libffi-dev libssl-dev -y

# Create project directory
echo "📁 Creating project directory..."
PROJECT_DIR="$HOME/secure-file-transfer"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Create virtual environment
echo "🌐 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python packages
echo "📚 Installing Python packages..."
pip install Flask==2.3.3
pip install Flask-Login==0.6.3
pip install Flask-WTF==1.1.1
pip install WTForms==3.0.1
pip install Werkzeug==2.3.7
pip install cryptography==41.0.4
pip install pyotp==2.9.0
pip install qrcode==7.4.2
pip install Pillow==10.0.0

# Install face recognition (this might take a while)
echo "👤 Installing face recognition libraries..."
pip install cmake
pip install dlib
pip install face-recognition==1.3.0

# Install other dependencies
pip install paramiko==3.3.1
pip install bcrypt==4.0.1
pip install python-dotenv==1.0.0
pip install opencv-python==4.8.1.78
pip install numpy==1.24.3

# Create necessary directories
echo "📂 Creating application directories..."
mkdir -p uploads
mkdir -p encrypted_files
mkdir -p face_encodings
mkdir -p templates
mkdir -p static

# Set proper permissions
chmod 755 uploads encrypted_files face_encodings

# Create systemd service file
echo "⚙️ Creating systemd service..."
sudo tee /etc/systemd/system/secure-file-transfer.service > /dev/null <<EOF
[Unit]
Description=Secure File Transfer Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin
ExecStart=$PROJECT_DIR/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Create nginx configuration (optional)
echo "🌐 Creating nginx configuration..."
sudo tee /etc/nginx/sites-available/secure-file-transfer > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com;  # Change this to your domain

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        client_max_body_size 100M;
    }
}
EOF

# Create environment file
echo "🔧 Creating environment configuration..."
cat > .env <<EOF
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
FLASK_ENV=production
FLASK_DEBUG=False
MAX_FILE_SIZE=104857600
ALLOWED_EXTENSIONS=*
FACE_RECOGNITION_TOLERANCE=0.6
FACE_DETECTION_MODEL=hog
TOTP_ISSUER_NAME=Secure File Transfer
TOTP_DIGITS=6
TOTP_INTERVAL=30
EOF

# Create startup script
echo "🚀 Creating startup script..."
cat > start.sh <<EOF
#!/bin/bash
cd "$PROJECT_DIR"
source venv/bin/activate
python app.py
EOF

chmod +x start.sh

# Install and configure firewall
echo "🔥 Configuring firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 5000/tcp
sudo ufw --force enable

# Enable and start the service
echo "🎯 Enabling service..."
sudo systemctl daemon-reload
sudo systemctl enable secure-file-transfer

echo ""
echo "✅ Installation completed!"
echo ""
echo "📋 Next Steps:"
echo "1. Copy your application files to: $PROJECT_DIR"
echo "2. Update the .env file with your settings"
echo "3. Start the service: sudo systemctl start secure-file-transfer"
echo "4. Check status: sudo systemctl status secure-file-transfer"
echo "5. View logs: sudo journalctl -u secure-file-transfer -f"
echo ""
echo "🌐 Access your application at: http://your-server-ip:5000"
echo ""
echo "🔒 Security Notes:"
echo "- Change the SECRET_KEY in .env"
echo "- Set up SSL/TLS certificates for production"
echo "- Configure your domain in nginx"
echo "- Consider setting up fail2ban for additional security"
echo ""
echo "💡 For developing countries:"
echo "- This runs on minimal hardware (1GB RAM, 1 CPU core)"
echo "- No cloud subscriptions required"
echo "- Can be deployed on local servers or cheap VPS"
echo "- Perfect for schools, small businesses, government offices"
echo ""

# Create a simple README
cat > README.md <<EOF
# Secure File Transfer

A cost-effective, secure file transfer solution designed for developing countries.

## Features
- 🔐 AES-256 encryption
- 👤 Facial recognition
- 📱 Two-factor authentication
- 🔍 File integrity verification
- 💰 No cloud costs

## Quick Start
1. Run: sudo systemctl start secure-file-transfer
2. Open: http://your-server:5000
3. Register and upload files

## Administration
- Service: sudo systemctl status secure-file-transfer
- Logs: sudo journalctl -u secure-file-transfer
- Config: Edit .env file

## Cost Benefits
- One-time setup cost
- No monthly subscriptions
- Runs on minimal hardware
- Perfect for developing countries
EOF

echo "📖 Created README.md with usage instructions"
echo ""
echo "🎉 Setup complete! Your secure file transfer system is ready to use."
