from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__, url_prefix='/blog')

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, author_id, created, title, description, body, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403, "Unauthorised to access post")

    return post

@bp.route('/')
def blog():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, description, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, description, body, author_id)'
                ' VALUES (?, ?, ?, ?)',
                (title, description, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.blog'))

    return render_template('blog/create.html')

@bp.route('/<int:id>', methods =['GET', 'POST'])
@login_required
def post(id):
    post = get_post(id, check_author=False)
    return render_template('blog/post.html', post=post)
    

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.' # NOTE: required input is already in form. This just prevents form bypass

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, description = ?, body = ?'
                ' WHERE id = ?',
                (title, description, body, id)
            )
            db.commit()
            return redirect(url_for('blog.blog'))

    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id) # Test that user is creator of post with default check_author to True
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.blog'))
