from flask import Blueprint, current_app, g, make_response, redirect, render_template, request, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from print3dstore.errors import RequestException
from print3dstore.wrapper_functions import error_handler
from print3dstore.blueprints.auth import login_required
from print3dstore.blueprints.forms.auth import ChangePasswordForm, ProfileForm
from print3dstore.models import User, db

bp = Blueprint("profile", __name__, url_prefix="/profile")

@bp.route("")
@error_handler
def info():
    if g.user is None:
        raise RequestException("Unauthorized", 401)
    return render_template("profile/profile.html")

@bp.route("/orders")
@error_handler
@login_required
def orders():
    if g.user is None:
        raise RequestException("Unauthorized", 401)
    
    return render_template("profile/orders.html")

@bp.route("/settings", methods=["GET", "POST"])
@error_handler
@login_required
def settings():
    if g.user is None:
        raise RequestException("Unauthorized", 401)

    address_form = ProfileForm()
    password_form = ChangePasswordForm()
    
    address_form.first_name.data = g.user.first_name
    address_form.last_name.data = g.user.last_name
    address_form.address_line1.data = g.user.address_line1
    address_form.address_line2.data = g.user.address_line2
    address_form.city.data = g.user.city
    address_form.postal_code.data = g.user.postal_code
    address_form.phone.data = g.user.phone

    if request.method == "POST":
        user = db.get_or_404(User, g.user.id)

        user.first_name = request.form["first_name"]
        user.last_name = request.form["last_name"]
        user.address_line1 = request.form["address_line1"]
        user.address_line2 = request.form["address_line2"]
        user.city = request.form["city"]
        user.postal_code = request.form["postal_code"]
        user.phone = request.form["phone"]

        db.session.commit()

        return redirect(url_for("profile.settings"))

    return render_template(
        "profile/settings.html",
        address_form=address_form,
        password_form=password_form
    )

@bp.route("/change-password", methods=["GET", "POST"])
@error_handler
@login_required
def change_password():
    if g.user is None:
        raise RequestException("Unauthorized", 401)

    password_form = ChangePasswordForm(request.form)

    if not password_form.validate():
        raise RequestException("New password fields must match", 400)

    if not check_password_hash(g.user.password, password_form.current_password.data):
        raise RequestException("Incorrect password", 400)
    
    user = db.get_or_404(User, g.user.id)
    user.password = generate_password_hash(password_form.new_password.data)
    db.session.commit()

    return redirect(url_for("profile.settings"))

