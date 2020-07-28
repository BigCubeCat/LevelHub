from werkzeug.security import generate_password_hash
from flask_mail import Mail
from flask import Flask, render_template, redirect, request, url_for
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from data import db_session
import os
from data.__all_models import *
from forms import *
from flask_mail import Message
from flask_restful import Api
from itsdangerous import URLSafeTimedSerializer

project_root = os.path.dirname(__file__)
template_path = os.path.join(project_root, './templates')
app = Flask(__name__, template_folder=template_path)
app.config["SECRET_KEY"] = "1737011737011731737011701111"
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = 'flaskmail10@gmail.com'
app.config['MAIL_DEFAULT_SENDER'] = 'flaskmail10@gmail.com'
app.config['MAIL_PASSWORD'] = '79yrTMeaTDpUhia'
app.config['SECURITY_PASSWORD_SALT'] = "0"
app.config['UPLOAD_FOLDER'] = './tmp'
login_manager = LoginManager()
login_manager.init_app(app)
mail = Mail(app)
api = Api(app)


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email


def send_email(subject, recipients, text_body):
    msg = Message(subject, sender=app.config["MAIL_DEFAULT_SENDER"], recipients=[recipients])
    msg.body = text_body
    with app.app_context():
        mail.send(msg)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=["GET", "POST"])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User()
        user.email = form.email.data
        user.nick = form.nick.data
        user.hashed_password = generate_password_hash(form.password.data)
        img = request.files.get('img')
        token = generate_confirmation_token(form.email.data)
        confirm_url = url_for('index_page',
                              token=token, _external=True)
        while True:
            try:
                send_email(f"Hello, {form.nick.data}", form.email.data,
                           confirm_url)
                break
            except Exception as error:
                print(error)
        session = db_session.create_session()
        session.add(user)
        session.commit()
        login_user(user, remember=form.remember_me.data)
        if img:
            path = os.path.join('static', f'avatars/{user.id}.png')
            img.save(path)
        return redirect('/')
    return render_template('register.html', title='Register', form=form)


@app.route('/')
@app.route('/index')
@app.route('/index/<token>')
def index_page(token=''):
    if token:
        if confirm_token(token) == current_user.email:
            session = db_session.create_session()
            user = session.query(User).get(current_user.id)
            user.confirm = True
            session.commit()
            current_user.confirm = True
    return render_template('index.html', title="CubeAdventureHub")


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', error=error), 404


@app.errorhandler(401)
def page_not_found(error):
    return render_template('401.html', error=error), 401


@app.errorhandler(403)
def page_not_found(error):
    return render_template('403.html', error=error), 403
