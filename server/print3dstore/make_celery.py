from print3dstore import create_app

flask_app = create_app()
celery_app = flask_app.extensions["celery"]
