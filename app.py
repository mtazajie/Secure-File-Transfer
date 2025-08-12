import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import pyotp
import qrcode
import io
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import json
import hashlib
from datetime import datetime
import paramiko
from dotenv import load_dotenv

# Try to import face detection libraries
try:
    import cv2
    import numpy as np
    FACE_DETECTION_AVAILABLE = True
    print("✅ Face detection available (OpenCV)")
    
    # Load OpenCV face detector
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
except ImportError:
    FACE_DETECTION_AVAILABLE = False
    print("⚠️ Face detection not available")

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ENCRYPTED_FOLDER'] = 'encrypted_files'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['ENCRYPTED_FOLDER'], exist_ok=True)
if FACE_DETECTION_AVAILABLE:
    os.makedirs('face_data', exist_ok=True)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User database file
USER_DB_FILE = 'users.json'

# In-memory user storage (loaded from JSON)
users_db = {}

class User(UserMixin):
    def __init__(self, id, username, password_hash, email=None, totp_secret=None, face_data=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.email = email
        self.totp_secret = totp_secret
        self.face_data = face_data

def load_users():
    """Load users from JSON file"""
    global users_db
    try:
        if os.path.exists(USER_DB_FILE):
            with open(USER_DB_FILE, 'r') as f:
                data = json.load(f)
                users_db = {}
                for user_id, user_data in data.items():
                    users_db[user_id] = User(
                        id=user_data['id'],
                        username=user_data['username'],
                        password_hash=user_data['password_hash'],
                        email=user_data.get('email'),
                        totp_secret=user_data.get('totp_secret'),
                        face_data=user_data.get('face_data')
                    )
            print(f"✅ Loaded {len(users_db)} users from database")
    except Exception as e:
        print(f"⚠️ Error loading users: {e}")
        users_db = {}

def save_users():
    """Save users to JSON file"""
    try:
        data = {}
        for user_id, user in users_db.items():
            data[user_id] = {
                'id': user.id,
                'username': user.username,
                'password_hash': user.password_hash,
                'email': user.email,
                'totp_secret': user.totp_secret,
                'face_data': user.face_data
            }
        with open(USER_DB_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Saved {len(users_db)} users to database")
    except Exception as e:
        print(f"⚠️ Error saving users: {e}")

@login_manager.user_loader
def load_user(user_id):
    return users_db.get(user_id)

def generate_key_from_password(password: str, salt: bytes = None) -> tuple:
    """Generate encryption key from password"""
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt

def encrypt_file(file_path: str, password: str) -> str:
    """Encrypt a file and return the encrypted file path"""
    with open(file_path, 'rb') as file:
        file_data = file.read()
    
    key, salt = generate_key_from_password(password)
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(file_data)
    
    # Create encrypted file
    encrypted_filename = f"encrypted_{os.path.basename(file_path)}.enc"
    encrypted_path = os.path.join(app.config['ENCRYPTED_FOLDER'], encrypted_filename)
    
    with open(encrypted_path, 'wb') as encrypted_file:
        encrypted_file.write(salt + encrypted_data)
    
    return encrypted_path

def decrypt_file(encrypted_path: str, password: str, output_path: str) -> bool:
    """Decrypt a file"""
    try:
        with open(encrypted_path, 'rb') as encrypted_file:
            salt = encrypted_file.read(16)
            encrypted_data = encrypted_file.read()
        
        key, _ = generate_key_from_password(password, salt)
        fernet = Fernet(key)
        decrypted_data = fernet.decrypt(encrypted_data)
        
        with open(output_path, 'wb') as output_file:
            output_file.write(decrypted_data)
        
        return True
    except Exception as e:
        print(f"Decryption error: {e}")
        return False

def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA-256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def detect_face_opencv(image_data):
    """Simple face detection using OpenCV"""
    if not FACE_DETECTION_AVAILABLE:
        return None
    
    # Convert image data to numpy array
    nparr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        return None
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    
    if len(faces) > 0:
        # Return the largest face
        largest_face = max(faces, key=lambda x: x[2] * x[3])
        x, y, w, h = largest_face
        face_img = gray[y:y+h, x:x+w]
        return face_img
    
    return None

def save_face_data(username: str, face_data):
    """Save face data to file"""
    if FACE_DETECTION_AVAILABLE and face_data is not None:
        face_path = f"face_data/{username}.npy"
        np.save(face_path, face_data)
        return True
    return False

def load_face_data(username: str):
    """Load face data from file"""
    if FACE_DETECTION_AVAILABLE:
        face_path = f"face_data/{username}.npy"
        if os.path.exists(face_path):
            return np.load(face_path)
    return None

def compare_faces(face1, face2):
    """Simple face comparison using template matching"""
    if not FACE_DETECTION_AVAILABLE or face1 is None or face2 is None:
        return False
    
    try:
        # Resize faces to same size
        face1_resized = cv2.resize(face1, (100, 100))
        face2_resized = cv2.resize(face2, (100, 100))
        
        # Calculate correlation coefficient
        result = cv2.matchTemplate(face1_resized, face2_resized, cv2.TM_CCOEFF_NORMED)
        similarity = result[0][0]
        
        # Threshold for face match (adjust as needed)
        return similarity > 0.6
    except:
        return False

@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('dashboard.html', face_recognition_available=FACE_DETECTION_AVAILABLE)
    return render_template('index.html', face_recognition_available=FACE_DETECTION_AVAILABLE)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if username or email already exists
        for user in users_db.values():
            if user.username == username:
                flash('Username already exists')
                return redirect(url_for('register'))
            if user.email == email:
                flash('Email already exists')
                return redirect(url_for('register'))
        
        # Generate TOTP secret
        totp_secret = pyotp.random_base32()
        
        # Create user
        user_id = str(len(users_db) + 1)
        password_hash = generate_password_hash(password)
        user = User(user_id, username, password_hash, email, totp_secret)
        users_db[user_id] = user
        
        # Save users to JSON file
        save_users()
        
        # Generate QR code for TOTP
        totp_uri = pyotp.totp.TOTP(totp_secret).provisioning_uri(
            name=username,
            issuer_name="Secure File Transfer"
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        qr_code_data = base64.b64encode(img_buffer.getvalue()).decode()
        
        session['temp_user_id'] = user_id
        
        if FACE_DETECTION_AVAILABLE:
            session['setup_step'] = 'face_setup'
            return render_template('setup_2fa.html', qr_code=qr_code_data, totp_secret=totp_secret)
        else:
            # Skip face setup if not available
            flash('Registration completed successfully! Please scan the QR code with your authenticator app, then login.')
            session.pop('temp_user_id', None)
            return render_template('setup_2fa.html', qr_code=qr_code_data, totp_secret=totp_secret, skip_face=True)
    
    return render_template('register.html', face_recognition_available=FACE_DETECTION_AVAILABLE)

@app.route('/setup_face', methods=['GET', 'POST'])
def setup_face():
    if not FACE_DETECTION_AVAILABLE:
        flash('Face detection is not available on this system')
        return redirect(url_for('login'))
        
    if 'temp_user_id' not in session or session.get('setup_step') != 'face_setup':
        return redirect(url_for('register'))
    
    if request.method == 'POST':
        # Handle face image upload
        if 'face_image' not in request.files:
            flash('No face image uploaded')
            return redirect(url_for('setup_face'))
        
        file = request.files['face_image']
        if file.filename == '':
            flash('No file selected')
            return redirect(url_for('setup_face'))
        
        # Process face image
        image_data = file.read()
        face_data = detect_face_opencv(image_data)
        
        if face_data is None:
            flash('No face detected in the image. Please upload a clear image.')
            return redirect(url_for('setup_face'))
        
        # Save face data
        user_id = session['temp_user_id']
        user = users_db[user_id]
        save_face_data(user.username, face_data)
        
        # Save users to JSON file
        save_users()
        
        flash('Registration completed successfully with face recognition!')
        session.pop('temp_user_id', None)
        session.pop('setup_step', None)
        
        return redirect(url_for('login'))
    
    return render_template('setup_face.html')

@app.route('/complete_registration')
def complete_registration():
    """Complete registration without face setup"""
    if 'temp_user_id' in session:
        session.pop('temp_user_id', None)
        session.pop('setup_step', None)
        flash('Registration completed successfully!')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        totp_code = request.form['totp_code']
        
        # Find user
        user = None
        for u in users_db.values():
            if u.username == username:
                user = u
                break
        
        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        
        # Verify TOTP
        totp = pyotp.TOTP(user.totp_secret)
        if not totp.verify(totp_code):
            flash('Invalid 2FA code')
            return redirect(url_for('login'))
        
        if FACE_DETECTION_AVAILABLE and load_face_data(user.username) is not None:
            session['pending_user_id'] = user.id
            return redirect(url_for('face_verification'))
        else:
            # Skip face verification if not available or not set up
            login_user(user)
            flash('Login successful!')
            return redirect(url_for('index'))
    
    return render_template('login.html', face_recognition_available=FACE_DETECTION_AVAILABLE)

@app.route('/face_verification', methods=['GET', 'POST'])
def face_verification():
    if not FACE_DETECTION_AVAILABLE:
        flash('Face detection is not available on this system')
        return redirect(url_for('login'))
        
    if 'pending_user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        if 'face_image' not in request.files:
            flash('No face image provided')
            return redirect(url_for('face_verification'))
        
        file = request.files['face_image']
        user_id = session['pending_user_id']
        user = users_db[user_id]
        
        # Process uploaded face image
        image_data = file.read()
        current_face = detect_face_opencv(image_data)
        
        if current_face is None:
            flash('No face detected. Please try again.')
            return redirect(url_for('face_verification'))
        
        # Load stored face data
        stored_face = load_face_data(user.username)
        if stored_face is None:
            flash('Face verification setup required')
            return redirect(url_for('login'))
        
        # Compare faces
        if compare_faces(stored_face, current_face):
            login_user(user)
            session.pop('pending_user_id', None)
            flash('Login successful with face verification!')
            return redirect(url_for('index'))
        else:
            flash('Face verification failed')
            return redirect(url_for('face_verification'))
    
    return render_template('face_verification.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        
        file = request.files['file']
        encryption_password = request.form['encryption_password']
        
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Calculate original file hash
            original_hash = calculate_file_hash(file_path)
            
            # Encrypt the file
            encrypted_path = encrypt_file(file_path, encryption_password)
            
            # Calculate encrypted file hash
            encrypted_hash = calculate_file_hash(encrypted_path)
            
            # Store file metadata
            file_metadata = {
                'original_filename': filename,
                'encrypted_filename': os.path.basename(encrypted_path),
                'original_hash': original_hash,
                'encrypted_hash': encrypted_hash,
                'upload_time': datetime.now().isoformat(),
                'uploader': current_user.username
            }
            
            # Save metadata
            metadata_path = encrypted_path + '.metadata'
            with open(metadata_path, 'w') as f:
                json.dump(file_metadata, f, indent=2)
            
            # Remove original file for security
            os.remove(file_path)
            
            flash(f'File {filename} uploaded and encrypted successfully!')
            return redirect(url_for('file_list'))
    
    return render_template('upload.html')

@app.route('/files')
@login_required
def file_list():
    encrypted_files = []
    for filename in os.listdir(app.config['ENCRYPTED_FOLDER']):
        if filename.endswith('.metadata'):
            metadata_path = os.path.join(app.config['ENCRYPTED_FOLDER'], filename)
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            encrypted_files.append(metadata)
    
    return render_template('file_list.html', files=encrypted_files)

@app.route('/download/<encrypted_filename>')
@login_required
def download_file(encrypted_filename):
    return render_template('download.html', encrypted_filename=encrypted_filename)

@app.route('/decrypt_download', methods=['POST'])
@login_required
def decrypt_download():
    encrypted_filename = request.form['encrypted_filename']
    decryption_password = request.form['decryption_password']
    
    encrypted_path = os.path.join(app.config['ENCRYPTED_FOLDER'], encrypted_filename)
    
    # Load metadata
    metadata_path = encrypted_path + '.metadata'
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    # Decrypt file to temporary location
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_{metadata['original_filename']}")
    
    if decrypt_file(encrypted_path, decryption_password, temp_path):
        # Verify file integrity
        decrypted_hash = calculate_file_hash(temp_path)
        if decrypted_hash == metadata['original_hash']:
            return send_file(temp_path, as_attachment=True, download_name=metadata['original_filename'])
        else:
            os.remove(temp_path)
            flash('File integrity check failed')
    else:
        flash('Decryption failed - incorrect password')
    
    return redirect(url_for('download_file', encrypted_filename=encrypted_filename))

if __name__ == '__main__':
    # Load existing users from JSON database
    load_users()
    
    print("🔐 Secure File Transfer Starting...")
    print(f"Face Detection: {'✅ Available (OpenCV)' if FACE_DETECTION_AVAILABLE else '❌ Not Available'}")
    print(f"💾 User Database: {len(users_db)} users loaded")
    print("🌐 Server starting at http://localhost:5000")
    print("🛡️ Perfect for developing countries - no cloud costs!")
    print("")
    print("📱 Remember to have your 2FA app ready:")
    print("   - Google Authenticator (recommended)")
    print("   - Microsoft Authenticator") 
    print("   - Authy")
    print("")
    app.run(debug=True, host='0.0.0.0', port=5000)
    print("🛡️ Perfect for developing countries - no cloud costs!")
    print("")
    print("📱 Remember to have your 2FA app ready:")
    print("   - Google Authenticator (recommended)")
    print("   - Microsoft Authenticator") 
    print("   - Authy")
    print("")
    app.run(debug=True, host='0.0.0.0', port=5000)
