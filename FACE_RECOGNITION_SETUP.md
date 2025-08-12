# Face Recognition Installation Guide for Windows

## The Problem
Face recognition libraries (`dlib` and `face-recognition`) require Visual Studio Build Tools on Windows to compile C++ extensions.

## Solutions (Choose One)

### Solution 1: Install Visual Studio Build Tools (Recommended for Development)

1. **Download Visual Studio Build Tools:**
   - Go to: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Download "Build Tools for Visual Studio 2022"

2. **Install with C++ components:**
   ```
   - Workload: C++ build tools
   - Individual components:
     * MSVC v143 compiler toolset
     * Windows 10/11 SDK (latest version)
     * CMake tools for Visual Studio
   ```

3. **After installation, restart command prompt and run:**
   ```bash
   pip install dlib
   pip install face-recognition
   pip install opencv-python
   ```

### Solution 2: Use Pre-compiled Wheels (Easiest)

```bash
# Install from pre-compiled wheels
pip install dlib-binary
pip install face-recognition
pip install opencv-python
```

### Solution 3: Use Conda (Alternative Package Manager)

1. **Install Miniconda:**
   - Download from: https://docs.conda.io/en/latest/miniconda.html

2. **Create environment and install:**
   ```bash
   conda create -n secure-transfer python=3.9
   conda activate secure-transfer
   conda install -c conda-forge dlib
   pip install face-recognition
   pip install -r requirements-basic.txt
   ```

### Solution 4: Docker (For Production)

Use the provided Dockerfile which handles all dependencies:

```bash
docker build -t secure-file-transfer .
docker run -p 5000:5000 secure-file-transfer
```

## Current Working Setup (Without Face Recognition)

Your application is currently running successfully with:
- ✅ AES-256 file encryption
- ✅ Two-factor authentication (2FA)
- ✅ Secure file upload/download
- ✅ File integrity verification
- ❌ Face recognition (can be added later)

## Testing the Application

1. **Access the application:**
   Open browser to: http://localhost:5000

2. **Register a new account:**
   - Enter username and password
   - Scan QR code with authenticator app (Google Authenticator, Authy)
   - Complete registration (face recognition will be skipped)

3. **Login:**
   - Enter credentials
   - Enter 2FA code from authenticator app
   - Skip face verification

4. **Upload and encrypt files:**
   - Select file to upload
   - Enter encryption password
   - File will be encrypted with AES-256

5. **Download and decrypt files:**
   - Select encrypted file
   - Enter decryption password
   - File integrity will be verified

## Production Deployment Options

### Option 1: Local Server (No Cloud Costs)
- Use old computer or Raspberry Pi
- Perfect for small businesses, schools
- One-time cost: $100-500

### Option 2: VPS Hosting
- DigitalOcean, Linode, Vultr: $5-20/month
- Much cheaper than cloud storage
- Full control over data

### Option 3: Shared Hosting
- Many web hosts support Python/Flask
- $10-30/month
- Good for small teams

## Security Features Currently Active

1. **Encryption:**
   - AES-256-CBC encryption
   - PBKDF2 key derivation (100,000 iterations)
   - Random salt for each file

2. **Authentication:**
   - Password-based login
   - TOTP two-factor authentication
   - Session management

3. **File Integrity:**
   - SHA-256 hashing
   - Tamper detection
   - Metadata verification

4. **Security Best Practices:**
   - Secure filename handling
   - Original files deleted after encryption
   - Environment-based configuration

## Cost Comparison (Annual)

**Traditional Cloud Solutions:**
- Dropbox Business: $1,800/year (10 users)
- Google Workspace: $1,440/year (10 users)
- OneDrive Business: $1,200/year (10 users)

**Our Solution:**
- Basic VPS: $240/year
- Domain name: $15/year
- SSL certificate: $0 (Let's Encrypt)
- **Total: $255/year (85% savings!)**

## Next Steps

1. **Test the current setup thoroughly**
2. **Deploy to production server**
3. **Add face recognition later (optional)**
4. **Set up backups and monitoring**
5. **Train users on the system**

The system is fully functional without face recognition and provides excellent security for developing countries where every dollar counts!
