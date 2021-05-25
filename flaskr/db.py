import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

# g is used for store data globally for context of each request (things that might be requested across functions for a request)
#       So that for example below, we don't have to re-establish connection with db every fn call   
#       https://flask.palletsprojects.com/en/1.1.x/api/#flask.g

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

# Close connection to db if it exists
#       However, we still need to register them with app. Since we using factory fn create_app instead, app is not available yet so we register with factory fn instead
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()
    print('Resetting DB...')

    # open_resource
    #       https://flask.palletsprojects.com/en/1.1.x/api/#flask.Flask.open_resource
    #       Open resource schema.sql in resource folder (I assume identified using relative path) to generate fresh empty tables
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

# create cmd line command "init-db" to call init_db() and echo message for success to user
@click.command('init-db')
@with_appcontext
def init_db_command():
    #Clear the existing data and create new tables.
    init_db()
    click.echo('Initialized the database.')

# So here, once we do have the app by calling create_app, we can register close_db and init_db_command with the app
def init_app(app):
    # https://flask.palletsprojects.com/en/1.1.x/api/#flask.Flask.teardown_appcontext
    #   tell flask to call close_db when popping context / cleaning up
    app.teardown_appcontext(close_db)
    
    app.cli.add_command(init_db_command)
