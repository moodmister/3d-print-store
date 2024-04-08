"""
Author: Valentin Stoyanov (v.stoyanov0069@gmail.com)
License: MIT
Date: 2024-03-29
"""
import os
from dotenv import dotenv_values
from flask import Flask

from print3dstore.cli import load_fixtures_command
from .models import db

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(dotenv_values(".env"))

    db.init_app(app)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    with app.app_context():
        db.create_all()

    from .blueprints import main, media, auth
    app.register_blueprint(main.bp)
    app.register_blueprint(media.bp)
    app.register_blueprint(auth.bp)

    app.cli.add_command(load_fixtures_command)

    return app
