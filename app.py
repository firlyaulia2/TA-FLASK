import uuid, pymysql, os, random
import numpy as np
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from ultralytics import YOLO
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_mail import Mail, Message

from routes.categories import categories_blueprint
from routes.detail import detail_blueprint
from routes.warna import warna_blueprint

app = Flask(__name__, static_folder='img')
CORS(app)

app.config['SECRET_KEY'] = 'prily'
app.config['JWT_SECRET_KEY'] = 'prily'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'skripsi'

db = pymysql.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD'],
    db=app.config['MYSQL_DB']
)
cursor = db.cursor()

jwt = JWTManager(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'afirlyaulia@gmail.com'
app.config['MAIL_PASSWORD'] = 'vuea elba bxze boxf'
app.config['MAIL_DEFAULT_SENDER'] = 'afirlyaulia@gmail.com'

mail = Mail(app)

# YOLO v8
model_path = 'E:/TA FIRLY/model/best.pt'
model = YOLO(model_path)

# YOLO v8 warna
model_path_warna = 'E:/TA FIRLY/model/warna.pt'
model_warna = YOLO(model_path_warna)

#klasifikasi
def classify_image(image_path):
    results = model(image_path)
    names_dict = results[0].names
    probs = results[0].probs.data.tolist()
    predicted_class = names_dict[np.argmax(probs)]
    return predicted_class

def classify_warna_image(image_path):
    results = model_warna(image_path)
    names_dict = results[0].names
    probs = results[0].probs.data.tolist()
    predicted_class = names_dict[np.argmax(probs)]
    return predicted_class

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def home():
    return render_template('index.html')

# ----Auth----

def insert_user(username, email, password):
    sql = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
    cursor.execute(sql, (username, email, password))
    db.commit()

def get_user(email):
    sql = "SELECT * FROM users WHERE email = %s"
    cursor.execute(sql, (email,))
    return cursor.fetchone()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if get_user(email):
        return jsonify({'error': 'Email sudah ada'}), 400

    password_hash = generate_password_hash(password)
    insert_user(username, email, password_hash)
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = get_user(email)
    if not user or not check_password_hash(user[3], password):
        return jsonify({'error': 'Invalid email or password'}), 401

    token = create_access_token(identity=email, additional_claims={"sub": email}, expires_delta=False)
    return jsonify({'token': token}), 200

@app.route('/logout', methods=['POST'])
def logout():
    return jsonify({'message': 'Logout successful'}), 200

otp_storage = {}

def generate_otp():
    return str(random.randint(100000, 999999))

@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    email = data.get('email')
    user = get_user(email)

    if not user:
        return jsonify({'error': 'Email tidak ditemukan'}), 404

    otp = generate_otp()
    otp_storage[email] = otp

    msg = Message('Your OTP Code', recipients=[email])
    msg.body = f'Your OTP code is {otp}'
    mail.send(msg)

    return jsonify({'message': 'OTP sent'}), 200

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')

    if otp_storage.get(email) == otp:
        return jsonify({'message': 'OTP verified'}), 200
    else:
        return jsonify({'error': 'Invalid OTP'}), 400

@app.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email')
    new_password = data.get('password')

    user = get_user(email)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    password_hash = generate_password_hash(new_password)
    sql = "UPDATE users SET password = %s WHERE email = %s"
    cursor.execute(sql, (password_hash, email))
    db.commit()

    return jsonify({'message': 'Password reset successful'}), 200

# -----

@app.route('/img/<path:filename>')
def send_file(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/yolo', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
         return jsonify({'error': 'No files uploaded'}), 400

    files = request.files.getlist('files')
    if not files:
        return jsonify({'error': 'No files uploaded'}), 400

    results = []

    for file in files:
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        unique_filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)

        predicted_class = classify_image(filepath)

        result = {
             'class': predicted_class
        }
        
        results.append(result)

    return jsonify(results)

@app.route('/yolo-warna', methods=['POST'])
def upload_warna_files():
    if 'files' not in request.files:
         return jsonify({'error': 'No files uploaded'}), 400

    files = request.files.getlist('files')
    if not files:
        return jsonify({'error': 'No files uploaded'}), 400

    results = []

    for file in files:
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        unique_filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)

        predicted_class = classify_warna_image(filepath)

        result = {
             'class': predicted_class
        }
        
        results.append(result)

    return jsonify(results)

app.register_blueprint(categories_blueprint)
app.register_blueprint(detail_blueprint)
app.register_blueprint(warna_blueprint)

if __name__ == "__main__":
    app.run(host="192.168.1.25",debug=True)