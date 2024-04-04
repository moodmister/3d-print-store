from wtforms import Form, FileField, validators

class UploadForm(Form):
    file = FileField('Models', validators=[validators.input_required()])
