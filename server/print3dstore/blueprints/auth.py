import functools
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for, make_response
from werkzeug.security import check_password_hash, generate_password_hash
from print3dstore.errors import RequestException
from print3dstore.models import Role, User, db
from print3dstore.wrapper_functions import error_handler
from .forms.auth import AuthForm

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/register", methods=["GET", "POST"])
@error_handler
def register():
    form = AuthForm(request.form)

    if request.method == "POST" and form.validate():
        email = request.form["email"]
        password = request.form["password"]
        error = ""

        if email == "":
            error += "Username is required. "
        if password == "":
            error += "Password is required. "

        if error == "":
            user_role = Role.query.filter_by(name="user").first()
            new_user = User(
                email=email,
                password=generate_password_hash(password),
                role_id=user_role.id,
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("auth.login"))
        else:
            raise RequestException(error, 400)
    return render_template("auth/user_form.html", form=form, action="register")


@bp.route("/login", methods=("GET", "POST"))
@error_handler
def login():
    form = AuthForm(request.form)
    if request.method == "POST" and form.validate():
        user = User.query.filter_by(email=request.form["email"]).first()
        if user is None:
            raise RequestException("User with that email is not found", 400)
        if not check_password_hash(user.password, request.form["password"]):
            raise RequestException("Incorrect password", 400)

        session["user_id"] = user.id

        redirect_to_url = url_for("main.root")
        if session["redirected_from_url"] is not None:
            redirect_to_url = session["redirected_from_url"]

        return redirect(redirect_to_url)

    return render_template("auth/user_form.html", form=form, action="login")


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter_by(id=user_id).first()
        g.roles = g.user.roles


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            session["redirected_from_url"] = request.url
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


@bp.route("/logout")
@error_handler
def logout():
    session.clear()
    g.user = None
    g.role = None
    return redirect(url_for("index"))
