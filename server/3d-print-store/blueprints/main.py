from flask import Blueprint, current_app, make_response, redirect, render_template, request

from forms.upload import UploadForm

bp = Blueprint("main", __name__)

@bp.route('/', methods=['GET'])
def root():
    upload_form = UploadForm()
    return render_template('home.html', form=upload_form)

@bp.route('/upload', methods=["POST"])
def upload():
    file = request.files['file']
    file.save(f"{current_app.root_path}/media/{file.filename}")

    return redirect('/')
