from flask import Blueprint, g, render_template

from print3dstore.wrapper_functions import error_handler
from print3dstore.errors import RequestException

bp = Blueprint("main", __name__)

@bp.route("/", methods=["GET"])
@error_handler
def root():
    return render_template("home.html")
