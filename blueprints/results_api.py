from flask import render_template, request, redirect, json, jsonify
from flask_restful import Resource, abort
import flask
from data import db_session
from data.__all_models import *
from flask_login import current_user
from forms import *
import requests
import os
import json


def abort_if_level_not_found(level_id):
    session = db_session.create_session()
    level = session.query(Level).get(level_id)
    if not level:
        abort(404, message=f"Level {level_id} not found")


blueprint = flask.Blueprint('results_api', __name__,
                            template_folder='templates')


def abort_if_result_not_found(result_id):
    session = db_session.create_session()
    result = session.query(Result).get(result_id)
    if not result:
        abort(404, message=f"Result {result_id} not found")


class ResultResource(Resource):
    def delete(self, result_id):
        abort_if_result_not_found(result_id)
        session = db_session.create_session()
        result = session.query(Result).get(result_id)
        session.delete(result)
        for res_app in session.query(ResultAppreciated).filter(ResultAppreciated.result_id
                                                               == result_id).all():
            session.delete(res_app)
        session.commit()
        return jsonify({'success': "OK"})


@blueprint.route('/button_like_result/<int:result_id>', methods=['GET', 'POST'])
def button_like(result_id):
    change_karma_on_result(result_id, 1)
    return json.dump({"data": "success"})


@blueprint.route('/button_dislike_result/<int:result_id>', methods=['GET', 'POST'])
def button_dislike(result_id):
    change_karma_on_result(result_id, -1)
    return json.dump({"data": "success"})


def change_karma_on_result(result_id, points):
    session = db_session.create_session()
    for re in session.query(ResultAppreciated).filter(ResultAppreciated.result_id == result_id):
        if re.user_id == current_user.id:
            return
    result = session.query(Result).get(result_id)
    result_appreciated = ResultAppreciated()
    result_appreciated.user_id = current_user.id
    result_appreciated.result_id = result.id
    session.query(Result).get(result_id).karma += points
    session.query(User).get(result.author).karma += points
    session.add(result_appreciated)
    session.commit()


@blueprint.route('/public_result', methods=["POST", "GET"])
def public_result():
    form = ResultForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        res = Result()
        res.author = current_user.id
        res.level_id = form.level.data
        session.add(res)
        session.commit()
        file = form.content.data
        path = os.path.abspath(os.path.join("./tmp", "tmp.result"))
        file.save(path)
        with open(path, 'r', encoding='utf-8') as result_file:
            score = eval(result_file.read())['score']
        session.query(Result).get(res.id).score = score
        session.commit()
        os.remove(path)
        return redirect('/')
    return render_template('add_result.html', form=form)


@blueprint.route('/level/<int:level_id>', methods=["POST", "GET"])
def levels_page(level_id):
    abort_if_level_not_found(level_id)
    session = db_session.create_session()
    level = session.query(Level).get(level_id)
    results = []
    for res in session.query(Result).filter(Result.level_id == level_id).all():
        results.append(res)
    return render_template('level.html', results=results, current_level=level)


@blueprint.route('/delete_result/<int:result_id>', methods=["POST", "GET"])
def delete_result_page(result_id):
    abort_if_result_not_found(result_id)
    session = db_session.create_session()
    result = session.query(Result).get(result_id)
    if request.method == "POST":
        requests.delete(ResultResource, result_id, _external=True)
        return redirect('/')
    if not current_user.is_authenticated:
        abort(401)
    if result.author == current_user.id:
        return render_template('delete_page.html', delete_text="This Result")
    abort(403)
