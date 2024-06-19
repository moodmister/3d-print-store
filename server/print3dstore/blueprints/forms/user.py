import re
from wtforms import Form, PasswordField, SelectField, SelectMultipleField, StringField, validators
from wtforms.widgets import Select

class UserForm(Form):
    def is_valid_email(form, field) -> bool:
        email_regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"

        return bool(re.fullmatch(email_regex, field.data))

    email = StringField(
        "Email",
        validators=[is_valid_email, validators.input_required()],
        render_kw={"class": "form-control", "autocomplete": "email"},
    )
    password = PasswordField(
        "Password",
        render_kw={"class": "form-control"},
    )
    roles = SelectMultipleField("Roles", render_kw={"class": "form-control", "autocomplete": "given-name"})
    first_name = StringField("First Name (optional)", render_kw={"class": "form-control", "autocomplete": "given-name"})
    last_name = StringField(
        "Last Name",
        validators=[validators.input_required()],
        render_kw={"class": "form-control", "autocomplete": "family-name"},
    )
    city = StringField("City (optional)", render_kw={"class": "form-control"})
    postal_code = StringField("Postal code (optional)", render_kw={"class": "form-control"})
    address_line1 = StringField("Address line 1 (optional)", render_kw={"class": "form-control"})
    address_line2 = StringField("Address line 2 (optional)", render_kw={"class": "form-control"})

    phone = StringField("Number (optional)", render_kw={"class": "form-control"})
