from flask import Blueprint, current_app, g, make_response, redirect, render_template, request, url_for

from print3dstore.errors import RequestException
from print3dstore.wrapper_functions import error_handler

bp = Blueprint("profile", __name__)

@bp.route("/profile")
@error_handler
def info():
    if g.user is None:
        raise RequestException("Unauthorized", 403)
    return render_template("profile.html")
