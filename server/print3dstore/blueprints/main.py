from flask import Blueprint, current_app, make_response, redirect, render_template, request, url_for

from print3dstore.wrapper_functions import error_handler
from print3dstore.errors import RequestException

from .forms.upload import UploadForm

bp = Blueprint("main", __name__)

@bp.route('/', methods=['GET'])
@error_handler
def root():
    return render_template('home.html')


@bp.route('/upload', methods=["POST"])
@error_handler
def upload():
    files = request.files.getlist('stl_models')
    for file in files:
        file.save(f"{current_app.root_path}/media/{file.filename}")

    return redirect(url_for('main.root'))
