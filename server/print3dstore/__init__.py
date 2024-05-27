"""
Author: Valentin Stoyanov (v.stoyanov0069@gmail.com)
License: MIT
Date: 2024-03-29
"""
import os
from dotenv import dotenv_values
from flask import Flask
from flask_migrate import Migrate
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.base import MenuLink

from celery import Celery, Task

from print3dstore.cli import load_fixtures_command
from print3dstore.admin.admin_views import AccessControlView, MaterialView, OrderView, PaymentGatewayView, PrinterView, RoleView, SpoolView, StlModelView, UserView
from .models import Material, Order, PaymentGateway, Printer, Role, Spool, StlModel, User, db

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(dotenv_values(".env"))
    celery_init_app(app)

    db.init_app(app)

    migrate = Migrate(app, db, f"{app.root_path}/migrations")

    from .blueprints import main, media, auth, profile, order, tasks
    app.register_blueprint(main.bp)
    app.register_blueprint(media.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(profile.bp)
    app.register_blueprint(order.bp)
    app.register_blueprint(tasks.bp)

    app.config["FLASK_ADMIN_FLUID_LAYOUT"] = True
    app.config["FLASK_ADMIN_SWATCH"] = "morph"

    admin = Admin(name=app.name, template_mode="bootstrap4", base_template="admin/custom_base.html")
    admin.menu().insert(0, MenuLink(name="Back to site", url="/"))

    admin.add_view(MaterialView(Material, db.session, endpoint="materials"))
    admin.add_view(PrinterView(Printer, db.session, endpoint="printers"))
    admin.add_view(SpoolView(Spool, db.session, endpoint="spools"))
    admin.add_view(OrderView(Order, db.session, endpoint="orders"))
    admin.add_view(StlModelView(StlModel, db.session, endpoint="stl-models"))
    admin.add_view(PaymentGatewayView(PaymentGateway, db.session, endpoint="payment-gateways"))
    admin.add_view(UserView(User, db.session, endpoint="users"))
    admin.add_view(RoleView(Role, db.session, endpoint="roles"))

    admin.init_app(app)

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

    app.cli.add_command(load_fixtures_command)

    return app


def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(
        dict(
            broker_url=app.config["CELERY_BROKER_URL"],
            result_backend=app.config["CELERY_RESULT_BACKEND"],
            task_ignore_result=app.config["CELERY_IGNORE_RESULT"],
        )
    )
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app
