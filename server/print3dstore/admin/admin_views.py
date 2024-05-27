import datetime
import json
import math
from flask import app, g
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm

from print3dstore.models import Order, Role
from print3dstore.errors import RequestException
from print3dstore.blueprints.forms.order import OrderEditForm, OrderForm

# TODO Add form properties to the views and customize what's necessary
# TODO Add example order and customize order view

class AccessControlView(ModelView):
    form_base_class = SecureForm

    def is_accessible(self):
        if g.user is None:
            return False
        return g.user.has_permission(Role.all_permissions[self.name]["read"]) or g.user.has_permission(Role.all_permissions["Superuser"])


class UserView(AccessControlView):
    column_list = [
        "id",
        "first_name",
        "last_name",
        "email",
        "password",
        "orders",
        "roles",
        "city",
        "postal_code",
        "address_line1",
        "address_line2",
        "phone",
    ]
    column_exclude_list = ["password",]
    column_searchable_list = ["first_name", "last_name", "email"]
    column_formatters = dict(
        roles=lambda _v, _c, m, _p: ", ".join(list(map(lambda user_role: user_role.role.name ,m.roles)))
    )


class OrderView(AccessControlView):
    # TODO fix order edit form
    column_list = [
        "user",
        "stl_models",
        "estimated_printing_time",
        "estimated_cost",
        "real_cost",
        "shipping_cost",
        "payment_gateway",
        "address",
        "status"
    ]
    column_formatters = dict(
        user=lambda _v, _c, m, _p: m.user.email,
        stl_models=lambda _v, _c, m, _p: list(
            map(
                lambda model: model.file.full_path[
                    model.file.full_path.rfind("/") + 1:
                ],
                m.stl_models
            )
        ),
        estimated_cost=lambda _v, _c, m, _p: list(
            map(
                lambda model: model.estimated_cost / 100.0 if model.estimated_cost else 0,
                m.stl_models
            )
        ),
        estimated_printing_time=lambda _v, _c, m, _p: math.fsum(map(
            lambda model: math.ceil(model.estimated_time / 3600) if model.estimated_time else 0,
            m.stl_models
        )),
        payment_gateway=lambda _v, _c, m, _p: m.payment_gateway.type,
        address=lambda _v, _c, m, _p: f"{m.user.city}, {m.user.address_line1}, {m.user.address_line2}"
    )

    def on_form_prefill(self, form, id):
        form.status.choices = [
            Order.Status.QUEUED,
            Order.Status.IN_PROGRESS,
            Order.Status.SHIPPED,
            Order.Status.FINISHED
        ]
        return super().on_form_prefill(form, id)

class MaterialView(AccessControlView):
    pass


class SpoolView(AccessControlView):
    column_formatters = dict(
        material=lambda _v, _c, m, _p: m.material.name
    )


class PaymentGatewayView(AccessControlView):
    pass


class PrinterView(AccessControlView):
    pass


class StlModelView(AccessControlView):
    column_formatters = dict(
        file=lambda _v, _c, m, _p: m.file.full_path[
                    m.file.full_path.rfind("/") + 1:
                ],
        material=lambda _v, _c, m, _p: m.material.name,
        estimated_cost=lambda _v, _c, m, _p: m.estimated_cost / 100.0 if m.estimated_cost else 0,
        estimated_time=lambda _v, _c, m, _p: str(datetime.timedelta(seconds=m.estimated_time)) if m.estimated_time else 0
    )

class RoleView(AccessControlView):
    column_list = [
        "name",
        "permissions",
        "users"
    ]
    column_formatters = dict(
        users=lambda _v, _c, m, _p: ", ".join(
            str(user) for user in map(lambda user_role: user_role.user.email, m.users)
        ),
        permissions=lambda _v, _c, m, _p: ", ".join(
            str(perm) for perm in json.loads(m.permissions)
        )
    )
