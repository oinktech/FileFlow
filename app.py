from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from models import db, User
import os
import bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
@login_required
def index():
    user_folder = os.path.join("data", current_user.username)
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            login_user(user)
            return redirect(url_for('index'))
        flash('登入失敗，請檢查用戶名和密碼。')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        new_user = User(username=username, password=hashed_password.decode('utf-8'))
        db.session.add(new_user)
        db.session.commit()
        flash('註冊成功，請登入。')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/api/folders', methods=['GET'])
@login_required
def get_folders():
    try:
        user_folder = os.path.join("data", current_user.username)
        folders = os.listdir(user_folder)
        return jsonify(folders), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/create_folder', methods=['POST'])
@login_required
def create_folder():
    folder_name = request.json.get('folder_name')
    user_folder = os.path.join("data", current_user.username, folder_name)

    try:
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)
            return jsonify({"message": "資料夾已建立", "folder_name": folder_name}), 201
        return jsonify({"error": "資料夾已存在"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/create_file', methods=['POST'])
@login_required
def create_file():
    file_name = request.json.get('file_name')
    user_folder = os.path.join("data", current_user.username, file_name)

    try:
        if not os.path.exists(user_folder):
            with open(user_folder, 'w') as f:
                f.write('')  # 創建一個空文件
            return jsonify({"message": "檔案已建立", "file_name": file_name}), 201
        return jsonify({"error": "檔案已存在"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/delete_item', methods=['DELETE'])
@login_required
def delete_item():
    item_name = request.json.get('item_name')
    user_folder = os.path.join("data", current_user.username, item_name)

    try:
        if os.path.exists(user_folder):
            if os.path.isdir(user_folder):
                os.rmdir(user_folder)  # 刪除資料夾
            else:
                os.remove(user_folder)  # 刪除檔案
            return jsonify({"message": "項目已刪除"}), 200
        return jsonify({"error": "項目未找到"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0", port=10000)
