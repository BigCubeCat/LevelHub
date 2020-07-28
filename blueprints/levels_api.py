from flask import render_template, redirect, json, jsonify, request
from flask_login import current_user
import flask
from data import db_session
from data.__all_models import *
from forms import LevelForm
import os
from flask_restful import abort, Resource
import requests
from app import api
from .results_api import ResultResource

blueprint = flask.Blueprint('levels_api', __name__,
                            template_folder='templates')


def abort_if_level_not_found(level_id):
    session = db_session.create_session()
    level = session.query(Level).get(level_id)
    if not level:
        abort(404, message=f"Level {level_id} not found")


class LevelResource(Resource):
    def delete(self, level_id):
        abort_if_level_not_found(level_id)
        session = db_session.create_session()
        level = session.query(Level).get(level_id)
        session.delete(level)
        session.commit()
        os.remove(os.path.abspath(f'static/levels/{level_id}.level'))
        for lev_app in session.query(LevelAppreciated).filter(
                LevelAppreciated.level_id == level_id).all():
            session.delete(lev_app)
        for res in session.query(Result).filter(Result.level_id == level_id).all():
            requests.delete(api.url_for(ResultResource, result_id=res.id, _external=True))
        session.commit()
        return jsonify({'success': "OK"})


@blueprint.route('/levels', methods=["POST", "GET"])
@blueprint.route('/levels/<string:sort_key>', methods=["POST", "GET"])
def levels_page(sort_key=''):
    session = db_session.create_session()
    levels = []
    for level in session.query(Level).filter(~Level.is_private):
        levels.append(level)
    if sort_key:
        if sort_key == "time":
            levels.sort(key=lambda lev: lev.modified_odate)
        elif sort_key == "top":
            levels.sort(key=lambda lev: -lev.karma)
    return render_template('levels.html', public_levels=levels)


@blueprint.route('/delete_level/<int:level_id>', methods=["POST", "GET"])
def delete_level_page(level_id):
    abort_if_level_not_found(level_id)
    session = db_session.create_session()
    level = session.query(Level).get(level_id)
    if request.method == 'POST':
        requests.delete(api.url_for(LevelResource, level_id=level_id, _external=True))
        return redirect('/')
    if not current_user.is_authenticated:
        abort(401)
    if level.author == current_user.id:
        return render_template('delete_page.html', delete_text="This Level")
    abort(403)


@blueprint.route('/add_level', methods=['POST', "GET"])
def create_level_page():
    form = LevelForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        level = Level()
        level.title = form.title.data
        level.hard = form.hard.data
        level.author = current_user.id
        level.is_private = form.is_private.data
        file = form.content.data
        session.add(level)
        session.commit()
        path = os.path.abspath(os.path.join("static/levels", f"{level.id}.level"))
        file.save(path)
        return redirect(f'/u/{current_user.id}')
    return render_template("add_level.html", form=form)


@blueprint.route('/button_like/<int:level_id>', methods=['GET', 'POST'])
def button_like(level_id):
    change_karma_on_level(level_id, 1)
    return json.dump({"data": "success"})


@blueprint.route('/button_dislike/<int:level_id>', methods=['GET', 'POST'])
def button_dislike(level_id):
    change_karma_on_level(level_id, -1)
    return json.dump({"data": "success"})


def change_karma_on_level(level_id, points):
    session = db_session.create_session()
    for la in session.query(LevelAppreciated).filter(LevelAppreciated.level_id == level_id):
        if la.user_id == current_user.id:
            return
    level = session.query(Level).get(level_id)
    level_appreciated = LevelAppreciated()
    level_appreciated.user_id = current_user.id
    level_appreciated.level_id = level.id
    session.query(Level).get(level_id).karma += points
    session.query(User).get(level.author).karma += points
    session.add(level_appreciated)
    session.commit()
