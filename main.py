from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, logout_user, LoginManager, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql

# Flask app setup
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/farmers'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Login manager setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) or Buyer.query.get(int(user_id))

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(1000), nullable=False)
    role = db.Column(db.String(50), default='user')

class Buyer(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(1000), nullable=False)
    role = db.Column(db.String(50), default='buyer')

class Register(db.Model):
    rid = db.Column(db.Integer, primary_key=True)
    farmername = db.Column(db.String(50), nullable=False)
    adharnumber = db.Column(db.String(50), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(50), nullable=False)
    phonenumber = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(50), nullable=False)
    farming = db.Column(db.String(50), nullable=False)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        password = generate_password_hash(request.form.get('password'), method='sha256')
        
        if User.query.filter_by(email=email).first() or Buyer.query.filter_by(email=email).first():
            flash("Email Already Exists", "warning")
            return redirect(url_for('signup'))
        
        new_user = Buyer(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Signup Success! Please Login", "success")
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first() or Buyer.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Login Success", "primary")
            return redirect(url_for('index'))
        
        flash("Invalid credentials", "warning")
        return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout Successful", "warning")
    return redirect(url_for('login'))

@app.route('/test')
def test():
    try:
        db.session.query("1").from_statement("SELECT 1").all()
        return 'Database Connected Successfully'
    except Exception as e:
        return f'Error Connecting to Database: {str(e)}'

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
