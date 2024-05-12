from wtforms import Form, FileField, FormField, HiddenField, IntegerField, Label, SelectField, StringField, TelField, validators
from wtforms.widgets import FileInput
from print3dstore.models import Material

from print3dstore.blueprints.forms.base import CsrfBaseForm

class OrderForm(CsrfBaseForm):
    order_heading = HiddenField(label="Order details")
    stl_models = FileField(
        label="Models",
        validators=[validators.input_required()],
        widget=FileInput(False),
        render_kw={"accept": ".stl", "class": "form-control"}
    )
    material = SelectField(
        label="Material",
        choices=[
            ("pla", "PLA"),
            ("petg", "PETG"),
            ("tpu", "TPU"),
        ],
        render_kw={"class": "form-select"}
    )
    color = SelectField(
        label="Color",
        choices=[
            ("red", "Red"),
            ("blue", "Blue"),
            ("green", "Green"),
        ],
        render_kw={"class": "form-select"}
    )
    delivery_heading = HiddenField(label="Delivery address details")
    city = StringField(
        label="City",
        validators=[validators.input_required()],
        render_kw={"class": "form-control"}
    )
    postal_code = StringField(
        label="Postal Code",
        validators=[validators.input_required()],
        render_kw={"class": "form-control"}
    )
    address_line1 = StringField(
        label="Address line 1",
        validators=[validators.input_required()],
        render_kw={"class": "form-control"}
    )
    address_line2 = StringField(
        label="Address line 2",
        validators=[validators.optional()],
        render_kw={"class": "form-control"}
    )
    phone = TelField(
        label="Phone number",
        render_kw={"class": "form-control"}
    )
    payment_heading = HiddenField(label="Payment")
    payment_method = SelectField(
        label="Payment method",
        validators=[validators.input_required()],
        choices=["Credit card", "Cash"],
        render_kw={"class": "form-select"}
    )
