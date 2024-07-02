import functools
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for, make_response
from werkzeug.security import check_password_hash, generate_password_hash
from psycopg2.errors import UniqueViolation
from print3dstore.errors import RequestException
from print3dstore.models import Role, User, UserRole, db
from print3dstore.wrapper_functions import error_handler
from .forms.auth import AuthForm, RegisterForm

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/register", methods=["GET", "POST"])
@error_handler
def register():
    form = RegisterForm()
    if request.method == "POST":
        form.process(request.form)
        if not form.validate():
            raise RequestException(form.errors, 400)
        email = request.form["email"]
        password = request.form["password"]
        errors = []

        if email == "":
            errors.append("Email is required.")
        if password == "":
            errors.append("Password is required.")

        user_email = db.session.execute(
            db.select(User).where(User.email == email)
        ).all()

        if len(user_email) > 0:
            flash("User with that email already exists", "danger")
            return redirect(url_for("auth.register"))

        if len(errors) == 0:
            role = db.session.scalar(
                db.select(Role).filter_by(name="user")
            )
            new_user = User(
                email=email,
                password=generate_password_hash(password),
                first_name=request.form["first_name"],
                last_name=request.form["last_name"],
                city=request.form["city"],
                postal_code=request.form["postal_code"],
                address_line1=request.form["address_line1"],
                address_line2=request.form["address_line2"],
                phone=request.form["phone"],
            )
            user_role = UserRole()
            user_role.user = new_user
            user_role.role = role
            db.session.add(new_user)
            db.session.add(user_role)
            db.session.commit()
            
            flash("User successfully registered.", "success")

            return redirect(url_for("auth.login"))
        else:
            raise RequestException(" ".join(errors), 400)

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
        if session.get("redirected_from_url") is not None:
            redirect_to_url = session["redirected_from_url"]

        flash("Successfully logged in", "success")

        return redirect(redirect_to_url)

    return render_template("auth/user_form.html", form=form, action="login")


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
        g.roles = None
    else:
        g.user = db.session.get(User, user_id)
        if g.user is None:
            session.clear()
            g.roles = None
        else:
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

    flash("Successfully logged out!", "success")

    return redirect(url_for("main.root"))
