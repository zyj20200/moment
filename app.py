from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Moment, Comment
from forms import LoginForm, RegisterForm
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///moments.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

API_URL = 'http://192.168.110.33:8888/gen'

@app.route('/')
def index():
    moments = Moment.query.order_by(Moment.timestamp.desc()).all()
    return render_template('index.html', moments=moments)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        # hashed_password = generate_password_hash(password, method='sha256')
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/post', methods=['POST'])
@login_required
def post_moment():
    content = request.form.get('content')
    if content:
        new_moment = Moment(user_id=current_user.id, content=content)
        db.session.add(new_moment)
        db.session.commit()

        # Call API to get comment content
        response = requests.post(API_URL, json={"message": content})
        if response.status_code == 200:
            comments = response.json().get('comment', [])
            for comment_text in comments:
                new_comment = Comment(moment_id=new_moment.id, text=comment_text)
                db.session.add(new_comment)
            db.session.commit()

    return redirect(url_for('index'))

@app.route('/moment/<int:moment_id>', methods=['GET', 'POST'])
@login_required
def view_moment(moment_id):
    moment = Moment.query.get_or_404(moment_id)
    if request.method == 'POST':
        comment_text = request.form.get('comment')
        if comment_text:
            new_comment = Comment(moment_id=moment.id, text=comment_text)
            db.session.add(new_comment)
            db.session.commit()
        return redirect(url_for('view_moment', moment_id=moment_id))
    return render_template('moment.html', moment=moment)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    # app.run(host="0.0.0.0", port=5000, debug=True)