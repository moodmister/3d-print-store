from wtforms import Form, PasswordField, StringField, validators

class AuthForm(Form):
    username = StringField("Username", validators=[validators.Length(min=4, max=25), validators.input_required()])
    password = PasswordField("Password", validators=[validators.input_required()])
