from flask import Flask, render_template, redirect, url_for, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.checkpw(password.encode('utf-8'), user.password):
            login_user(user)
            return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/api/create_folder', methods=['POST'])
@login_required
def create_folder():
    folder_name = request.json.get('folder_name')
    user_folder_path = os.path.join('data', current_user.username)
    
    if not os.path.exists(user_folder_path):
        os.makedirs(user_folder_path)

    folder_path = os.path.join(user_folder_path, folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        return jsonify({"message": "資料夾已創建成功!"})
    else:
        return jsonify({"error": "資料夾已存在!"})

@app.route('/api/folders')
@login_required
def folders():
    user_folder_path = os.path.join('data', current_user.username)
    if not os.path.exists(user_folder_path):
        return jsonify([])

    folders = [f for f in os.listdir(user_folder_path) if os.path.isdir(os.path.join(user_folder_path, f))]
    return jsonify(folders)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True,host="0.0.0.0", port=10000)
