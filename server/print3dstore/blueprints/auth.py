import functools
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for, make_response
from werkzeug.security import check_password_hash, generate_password_hash
from print3dstore.errors import RequestException
from print3dstore.models import Role, User, db
from .forms.auth import AuthForm

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/register", methods=["GET", "POST"])
def register():
    form = AuthForm(request.form)

    if request.method == "POST" and form.validate():
        username = request.form["username"]
        password = request.form["password"]
        error = ""

        if username == "":
            error += "Username is required. "
        if password == "":
            error += "Password is required. "

        if error == "":
            user_role = Role.query.filter_by(name="user").first()
            new_user = User(
                username=username,
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
def login():
    form = AuthForm(request.form)
    if request.method == "POST" and form.validate():
        user = User.query.filter_by(username=request.form["username"]).first()
        if user is None:
            message = "User not found"
            code = 404
            return make_response(
                render_template("error.html", message=message, code=code), code
            )
        if not check_password_hash(user.password, request.form["password"]):
            message = "Invalid password"
            code = 403
            return make_response(
                render_template("error.html", message=message, code=code), code
            )
        print("==============================")
        print(user.role_id)
        print("==============================")
        session["user_id"] = user.id
        session["role_id"] = user.role_id

        return redirect(url_for("index"))

    return render_template("auth/user_form.html", form=form, action="login")


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter_by(id=user_id).first()
        g.role = Role.query.filter_by(id=g.user.role_id).first()


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


@bp.route("/logout")
def logout():
    session.clear()
    g.user = None
    g.role = None
    return redirect(url_for("index"))
