from flask import Blueprint, current_app, make_response, redirect, render_template, request, url_for

from print3dstore.wrapper_functions import error_handler
from print3dstore.errors import RequestException

from .forms.upload import UploadForm

bp = Blueprint("order", __name__)

@bp.route("/order", methods=["GET", "POST"])
@error_handler
def order():
    if request.method == "POST":
        return redirect(url_for("main.root"))
    
    form = UploadForm()
    return render_template("order.html", form=form)

