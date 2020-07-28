import flask
import requests
from flask import render_template, redirect, request, jsonify
from flask_login import login_user, current_user
from flask_restful import abort, Resource
from data import db_session
from data.__all_models import *
from forms import *
import os
from app import api
from .levels_api import LevelResource
from .results_api import ResultResource

blueprint = flask.Blueprint('user_api', __name__,
                            template_folder='templates')


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


def check_my_id(user_id):
    if not current_user.is_authenticated:
        abort(401)
    if current_user.id != user_id:
        abort(403)


class UserResource(Resource):
    def get(self, user_id):
        session = db_session.create_session()
        abort_if_user_not_found(user_id)
        user = session.query(User).get(user_id)
        return jsonify(
            {
                'user': user.to_dict(only=('nick', 'karma', 'modified_date'))
            }
        )

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        for level in session.query(Level).filter(Level.author == user_id).all():
            requests.delete(api.url_for(LevelResource, level_id=level.id, _external=True))
        for res in session.query(Result).filter(Result.author == user_id).all():
            requests.delete(api.url_for(ResultResource, result_id=res.id, _external=True))
        return jsonify({'success': "OK"})


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Incorrect password",
                               form=form)
    return render_template('login.html', title='Login', form=form)


@blueprint.route('/u/<int:users_id>', methods=["POST", "GET"])
def user_page(users_id):
    abort_if_user_not_found(users_id)
    user_params = requests.get(api.url_for(UserResource, user_id=users_id, _external=True)).json()[
        'user']
    session = db_session.create_session()
    levels = []
    for level in session.query(Level).filter(Level.author == users_id):
        levels.append(level)
    return render_template('home_page.html', user_id=users_id, user_karma=user_params['karma'],
                           user_nick=user_params['nick'], user_levels=levels,
                           user_modified_date=user_params['modified_date'])


@blueprint.route('/change_password/<int:_id>', methods=["POST", "GET"])
def change_user_page(_id):
    form = ChangePasswordForm()
    if request.method == "POST":
        session = db_session.create_session()
        user = session.query(User).get(_id)
        user.set_password(form.password.data)
        session.commit()
        return redirect(f'/u/{_id}')
    return render_template('/change_password.html', form=form, _id=_id)


@blueprint.route('/change_image/<int:_id>', methods=["GET", "POST"])
def change_image(_id):
    check_my_id(_id)
    if request.method == "POST":
        img = request.files.get('img')
        if img:
            path = os.path.abspath(os.path.join('static', f'avatars/{_id}.png'))
            img.save(path)
            return redirect(f'/u/{_id}')
    return render_template('/change_image.html', _id=_id)


@blueprint.route('/change_nick/<int:_id>', methods=["GET", "POST"])
def change_nick(_id):
    form = ChangeNickForm()
    check_my_id(_id)
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).get(_id)
        user.nick = form.nick.data
        session.commit()
        return redirect(f'/u/{_id}')
    return render_template('/change_nick.html', _id=_id, form=form)


@blueprint.route('/delete_account/<int:user_id>', methods=["POST", "GET"])
def delete_user_by_id(user_id):
    check_my_id(user_id)
    if request.method == "POST":
        requests.delete(api.url_for(UserResource, user_id=user_id, _external=True))
        return redirect('/')
    return render_template('delete_page.html', delete_text="My Account")
