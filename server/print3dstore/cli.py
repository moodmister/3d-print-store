import click
from print3dstore.models import db, User, Role, UserRole
from werkzeug.security import generate_password_hash
import json

@click.command('load-fixtures')
def load_fixtures_command():
    click.echo("Creating admin user with 'admin' password.")
    email = "admin@mail.com"
    password = "admin"
    permissions = {
        "superuser": True
    }

    user = User(email=email, password=generate_password_hash(password))
    role = Role(name="superuser", permissions=json.dumps(permissions))

    userRole = UserRole()
    userRole.user = user
    userRole.role = role

    db.session.add(user)
    db.session.add(role)
    db.session.add(userRole)

    db.session.commit()
    click.echo("Superuser admin with password 'admin' has been created successfully.")


@click.command("first-start")
def first_load_command():
    click.echo("==Enter parameters for the admin user==")
    email = click.prompt("Enter email:", type=str)
    password = click.prompt("Enter password:", type=str)
    permissions = {
        "superuser": True
    }

    user = User(email=email, password=generate_password_hash(password))
    role = Role(name="superuser", permissions=json.dumps(permissions))

    userRole = UserRole()
    userRole.user = user
    userRole.role = role

    db.session.add(user)
    db.session.add(role)
    db.session.add(userRole)

    db.session.commit()
    click.echo("User admin with password 'admin' has been created successfully.")
