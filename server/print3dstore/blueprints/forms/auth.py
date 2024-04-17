from wtforms import Form, PasswordField, StringField, validators
import re


class AuthForm(Form):
    def is_valid_email(form, field) -> bool:
        email_regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"

        return bool(re.fullmatch(email_regex, field.data))

    email = StringField("Email", validators=[is_valid_email, validators.input_required()])
    password = PasswordField("Password", validators=[validators.input_required()])
