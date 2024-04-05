from wtforms import Form, FileField, validators
from wtforms.widgets import FileInput

class UploadForm(Form):
    stl_models = FileField('Models', validators=[validators.input_required()], widget=FileInput(True))
