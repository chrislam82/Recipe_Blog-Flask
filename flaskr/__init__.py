# Recipe Blog
# Reference:
#       https://flask.palletsprojects.com/en/1.1.x/

from flask import (
  Flask,
  redirect,
  url_for
)
import os
from flaskr.auth import login_required

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
        # https://flask.palletsprojects.com/en/1.1.x/config/#instance-folders
        # Instance folder contains things that we might want to modify in runtime
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        # Config contains things that overwrites default values for deployment
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    # Just doing the registering of functions with app (See comments in db.py)
    db.init_app(app)

    # a simple page that says hello
    @app.route('/', methods=['GET'])
    @login_required
    def index ():
      return redirect(url_for('blog.blog'))

    # Register blueprint in auth.py with app factory function
    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)

    # https://flask.palletsprojects.com/en/1.1.x/api/#flask.Flask.add_url_rule
    #       Register index with '/' so that they refer to the same things
    #           Remember, blog.py has no prefix in URL, so index route for blog.py is just /
    #           index is used elsewhere to also refer to the index, so we connect them together since they are the same things
    app.add_url_rule('/', endpoint='index')

    return app
