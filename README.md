# Secure File Transfer

A comprehensive, cost-effective secure file transfer solution designed specifically for developing countries where cloud services are expensive. This system provides enterprise-grade security without recurring subscription costs.

## 🌟 Features

### Security Features
- **🔐 AES-256 Encryption**: Military-grade encryption for all files
- **👤 Facial Recognition**: Biometric authentication using advanced face recognition
- **📱 Two-Factor Authentication (2FA)**: TOTP-based authentication compatible with Google Authenticator, Authy, etc.
- **🔍 File Integrity Verification**: SHA-256 hashing ensures files haven't been tampered with
- **🔑 PBKDF2 Key Derivation**: Secure password-based encryption key generation
- **🛡️ Multi-layer Security**: Three-factor authentication (password + 2FA + face recognition)

### Technical Features
- **🌐 Web-based Interface**: Beautiful, responsive HTML/CSS frontend
- **⚡ Flask Backend**: Lightweight Python Flask server
- **📁 SFTP Support**: Built-in SFTP capabilities for network transfers
- **💾 Local Storage**: No dependency on expensive cloud services
- **📊 File Management**: Upload, encrypt, decrypt, and download files securely

### Cost Benefits
- **💰 Zero Recurring Costs**: No monthly cloud subscriptions
- **🖥️ Minimal Hardware**: Runs on basic hardware (1GB RAM, 1 CPU core)
- **🌍 Perfect for Developing Countries**: Designed for budget-conscious organizations
- **🏢 Self-hosted**: Complete control over your data

## 🎯 Target Users

This solution is perfect for:
- 🏫 Educational institutions
- 🏥 Healthcare providers
- ⚖️ Legal firms
- 🏛️ Government offices
- 🏪 Small businesses
- 👤 Personal use

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Ubuntu/Debian Linux (recommended)
- Basic server or VPS

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/secure-file-transfer.git
cd secure-file-transfer
```

2. **Run the installation script:**
```bash
chmod +x install.sh
./install.sh
```

3. **Manual installation (alternative):**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir uploads encrypted_files face_encodings

# Copy environment file
cp .env.example .env
```

4. **Start the application:**
```bash
python app.py
```

5. **Access the application:**
Open your browser and go to `http://localhost:5000`

## 🔧 Configuration

### Environment Variables
Edit the `.env` file to customize your installation:

```bash
SECRET_KEY=your-very-secure-secret-key
FLASK_ENV=production
MAX_FILE_SIZE=104857600  # 100MB
FACE_RECOGNITION_TOLERANCE=0.6
TOTP_ISSUER_NAME=Secure File Transfer
```

### SFTP Configuration (Optional)
To enable SFTP transfers, add these to your `.env`:

```bash
SFTP_HOST=your-sftp-server.com
SFTP_PORT=22
SFTP_USERNAME=your-username
SFTP_PRIVATE_KEY_PATH=/path/to/private/key
```

## 📱 User Guide

### Registration Process
1. **Create Account**: Enter username and password
2. **Setup 2FA**: Scan QR code with authenticator app
3. **Face Registration**: Upload a clear photo for facial recognition

### Login Process
1. **Enter Credentials**: Username and password
2. **2FA Code**: Enter code from authenticator app
3. **Face Verification**: Take a photo or upload image for verification

### File Operations
1. **Upload**: Select file, enter encryption password, upload
2. **View Files**: See all your encrypted files with hashes
3. **Download**: Enter decryption password to download file

## 🔒 Security Details

### Encryption Process
1. File is uploaded to server
2. AES-256 encryption applied with user password
3. PBKDF2 key derivation with random salt
4. SHA-256 hash calculated for integrity
5. Original file securely deleted

### Authentication Layers
1. **Password**: Traditional username/password
2. **2FA**: Time-based one-time password (TOTP)
3. **Biometric**: Facial recognition verification

### File Integrity
- SHA-256 hash calculated on upload
- Hash verified on download
- Tampering detection built-in

## 🌐 Production Deployment

### Using systemd (Linux)
```bash
# Service will be created by install.sh
sudo systemctl start secure-file-transfer
sudo systemctl enable secure-file-transfer
sudo systemctl status secure-file-transfer
```

### Using Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app.py"]
```

### Nginx Reverse Proxy
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        client_max_body_size 100M;
    }
}
```

## 💡 Cost Comparison

### Traditional Cloud Solutions
- **Dropbox Business**: $15/user/month
- **Google Workspace**: $12/user/month
- **OneDrive Business**: $10/user/month
- **Annual Cost (10 users)**: $1,200 - $1,800

### Our Solution
- **One-time Setup**: $50-100 (VPS)
- **Annual Cost**: $200-400 (server hosting)
- **Savings**: 70-80% cost reduction
- **Additional Benefits**: Complete data control, enhanced security

## 🛠️ Development

### Project Structure
```
secure-file-transfer/
├── app.py                 # Main Flask application
├── sftp_manager.py        # SFTP functionality
├── requirements.txt       # Python dependencies
├── install.sh            # Installation script
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── upload.html
│   └── ...
├── uploads/              # Temporary file storage
├── encrypted_files/      # Encrypted file storage
└── face_encodings/       # Face recognition data
```

## 🔧 Troubleshooting

### Common Issues

**Face recognition installation fails:**
```bash
sudo apt install build-essential cmake
sudo apt install libopenblas-dev liblapack-dev
pip install dlib
```

**Permission errors:**
```bash
chmod 755 uploads encrypted_files face_encodings
```

**Port already in use:**
```bash
sudo lsof -i :5000
# Kill the process or change port in app.py
```

### Logs and Monitoring
```bash
# View service logs
sudo journalctl -u secure-file-transfer -f

# Check application logs
tail -f app.log

# Monitor system resources
htop
```

## 🤝 Contributing

We welcome contributions! Please:
1. Read the contributing guidelines
2. Fork the repository
3. Create a feature branch
4. Make your changes
5. Add tests if applicable
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Flask** - Web framework
- **face_recognition** - Facial recognition library
- **cryptography** - Encryption library
- **pyotp** - 2FA implementation
- **Bootstrap** - UI framework

## 🌍 Impact

This project aims to democratize secure file transfer by providing:
- Affordable solutions for developing countries
- Enterprise-grade security without enterprise costs
- Complete data sovereignty
- Educational opportunities in cybersecurity

## 📈 Future Roadmap

- [ ] Mobile app development
- [ ] Advanced user management
- [ ] Audit logging
- [ ] File sharing capabilities
- [ ] API development
- [ ] Multi-language support
- [ ] Database integration
- [ ] Backup and recovery features

---

**Made with ❤️ for developing countries worldwide**

*Empowering secure communication without breaking the budget*