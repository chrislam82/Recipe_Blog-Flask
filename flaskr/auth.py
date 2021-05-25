import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

# View functions are functions called to respond to requests
# Blueprints are used to organise views and other code
#       views >>registered to>> blueprints >>registered to app inside application factory

# flask.Blueprint
#       https://flask.palletsprojects.com/en/1.1.x/api/#flask.Blueprint
#       
#       Register a Blueprint called auth, defined at __name__, and attach prefix to associated URLs
#           Here, we are creating a blueprint to store all views related to authentication

bp = Blueprint('auth', __name__, url_prefix='/auth')

# Basically calling register view at URL /auth/register for a GET/POST request
#   If GET request on page, then user is just redirecting to it
#       Hence, it just returns the html template
#   If POST, process everything and if ok, insert into DB and redirect to login
#       Else just refresh /auth/register since invalid input somewhere
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:# Fetches 1 row with username = username. If not None, then there is a corresponding row, hence taken
            error = 'User {} is already registered.'.format(username)

        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            # https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.commit
            #       Need to commit changes to make changes visible to other db connections
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        # https://flask.palletsprojects.com/en/1.1.x/api/#flask.session
        #   session is a dict used to store data across requests
        #   So we set id in session as user_id and clear any potential residual data
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('blog.blog'))

        flash(error)

    return render_template('auth/login.html')

# Run fn before any views are called (auth views I believe)
#       Basically load user_id from session into global context (g)
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

# So that load_logged_in_user() doesnt load a user before any auth requests
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

# Decorator for any authentication views
#       Redirect if user not loaded in g
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
