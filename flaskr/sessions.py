from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from utils import get_session_json
import os

bp = Blueprint('sessions', __name__)

@bp.route('/')
@login_required
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, session_name, session_id, created, author_id, username'
        ' FROM session p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('sessions/index.html', posts=posts)

@bp.route('/load',methods=('GET', 'POST'))
@login_required
def load():
    if request.method == 'POST':
        #session_name = request.form['session_name']
        session_id = request.form['session_id']
        error = None

        if not session_id:
            error = 'Session ID is required.'

        if error is not None:
            flash(error)
        else:
            ## first api call

            json  = get_session_json(session_id)


            db = get_db()
            db.execute(
                'INSERT INTO session (session_name, session_id, author_id)'
                ' VALUES (?, ?, ?)',
                (json["name"], session_id, g.user['id'])
            )
            db.commit()
            return redirect(url_for('sessions.index'))

    return render_template('sessions/load.html')



@bp.route('/<session_id>/inspect', methods=('GET', 'POST'))
@login_required
def inspect(session_id):
    # TODO: 1. check with database whether id exists
    #       2. would be nice to store trial names and ids in database on first request instead of
    #           having two api calls.


    # filthy hack instead of a proper database
    json_path = session_id + ".json"
    import json

    if json_path in os.listdir(os.curdir):
        with open(json_path) as ifile:
            data = json.load(ifile)
    else:
        data = get_session_json(session_id)

    trials = data["trials"]
    return render_template('trials/t_index.html', trials=trials)

@bp.route('/<trial_name>/show_videos')
@login_required
def show_videos(trial_name):
    trial_path = os.path.join("Videos","160780df-d8c1-4fe9-af56-2219693ea48d",trial_name)
    videos = []
    for item in os.listdir(trial_path):
        if os.path.isdir(os.path.join(trial_path,item)):
            videos.extend(os.listdir(os.path.join(trial_path,item)))
        else:
            videos.append(os.path.join(trial_path,item))
            return render_template("trials/videos.html",videos=videos)
@bp.route('/display/<filename>')
def display_video(filename):

	return redirect(url_for('static', filename= filename), code=301)