from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from utils import get_session_json

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