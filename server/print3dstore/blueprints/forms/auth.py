from wtforms import Form, PasswordField, StringField, validators
import re


class AuthForm(Form):
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
        validators=[validators.input_required()],
        render_kw={"class": "form-control"},
    )


class ProfileForm(Form):
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

class RegisterForm(AuthForm, ProfileForm):
    pass


class ChangePasswordForm(Form):
    new_password = PasswordField(
        "New password",
        validators=[validators.input_required()],
        render_kw={"class": "form-control", "autocomplete": "new-password"},
    )
    retype_password = PasswordField(
        "Retype new password",
        validators=[validators.input_required()],
        render_kw={"class": "form-control", "autocomplete": "off"},
    )

    current_password = PasswordField(
        "Current password",
        validators=[validators.input_required()],
        render_kw={"class": "form-control", "autocomplete": "current-password"},
    )

    def validate(self, extra_validators = None) -> bool:
        if self.new_password.data != self.retype_password.data:
            return False

        return super().validate(extra_validators)
