import datetime
import json
import math
from flask import app, g, make_response, redirect, render_template, request, url_for
from flask_admin import BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm

from print3dstore.models import Material, PaymentGateway, StlModel, db, Order, Role, Spool
from print3dstore.errors import RequestException
from print3dstore.blueprints.forms.order import OrderEditForm, OrderForm
from print3dstore.wrapper_functions import error_handler

# TODO Add form properties to the views and customize what's necessary
# TODO Add example order and customize order view

class AnalyticsView(BaseView):
    @expose("/")
    def index(self):
        spools = db.session.scalars(db.select(Spool)).all()
        orders = db.session.scalars(db.select(Order)).all()
        return self.render('admin/analytics.html', spools=spools, orders=orders)

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
    can_create = False
    form = OrderEditForm
    column_list = [
        "user",
        "stl_models",
        # "estimated_printing_time",
        # "estimated_cost",
        # "real_cost",
        # "shipping_cost",
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
        # estimated_cost=lambda _v, _c, m, _p: list(
        #     map(
        #         lambda model: model.estimated_cost / 100.0 if model.estimated_cost else 0,
        #         m.stl_models
        #     )
        # ),
        # estimated_printing_time=lambda _v, _c, m, _p: math.fsum(map(
        #     lambda model: math.ceil(model.estimated_time / 3600) if model.estimated_time else 0,
        #     m.stl_models
        # )),
        payment_gateway=lambda _v, _c, m, _p: m.payment_gateway.type,
        address=lambda _v, _c, m, _p: f"{m.user.city}, {m.user.address_line1}, {m.user.address_line2}"
    )

    def on_form_prefill(self, form, id):
        order = db.get_or_404(Order, id)
        materials = db.session.scalars(db.select(Material)).all()
        spools = db.session.scalars(db.select(Spool)).all()
        payment_gateways = db.session.scalars(db.select(PaymentGateway)).all()
        stl_models = db.session.scalars(db.select(StlModel)).all()
        
        form_material_choices = list()
        for material in materials:
            option = (material.id, material.name)
            form_material_choices.append(option)

        form.material.choices = form_material_choices
        form.material.process_data(order.stl_models[0].material_id)

        form_color_choices = list()
        for spool in spools:
            form_color_choices.append(spool.color)

        form.color.choices = form_color_choices
        form.color.process_data(order.stl_models[0].color)

        form_payment_gateway_choices = list()
        for payment_gateway in payment_gateways:
            option = (payment_gateway.id, f"{payment_gateway.name} - {payment_gateway.type}")
            form_payment_gateway_choices.append(option)

        form.payment_method.choices = form_payment_gateway_choices
        form.payment_method.process_data(order.payment_gateway_id)

        form.city.data = order.user.city
        form.postal_code.data = order.user.postal_code
        form.address_line1.data = order.user.address_line1
        form.address_line2.data = order.user.address_line2
        form.phone.data = order.user.phone

        form.status.choices = [
            Order.Status.FINISHED,
            Order.Status.IN_PROGRESS,
            Order.Status.QUEUED,
            Order.Status.SHIPPED,
        ]
        form.status.process_data(order.status)

        return super().on_form_prefill(form, id)

    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        if request.method == "POST":
            order = db.get_or_404(Order, request.args.get("id"))

            form = OrderEditForm()
            self.on_form_prefill(form, order.id)
            form.process(request.form)
            if not form.validate():
                exception = RequestException(form.errors, 500)
                return make_response(
                    render_template('error.html', error=exception),
                    exception.http_code
                )


            order.stl_models[0].material_id = request.form.get("material")
            order.stl_models[0].color = request.form.get("color")

            order.user.city = request.form.get("city")
            order.user.postal_code = request.form.get("postal_code")
            order.user.phone = request.form.get("phone")
            order.user.address_line1 = request.form.get("address_line1")
            order.user.address_line2 = request.form.get("address_line2")
            
            order.payment_gateway_id = request.form.get("payment_method")
            order.status = request.form.get("status")

            db.session.commit()

            return redirect("/admin/orders/")
        return super().edit_view()


class MaterialView(AccessControlView):
    pass


class SpoolView(AccessControlView):
    column_list = [
        "make",
        "material",
        "color",
        "grams",
        "grams_left"
    ]
    column_formatters = dict(
        material=lambda _v, _c, m, _p: m.material.name
    )


class PaymentGatewayView(AccessControlView):
    pass


class PrinterView(AccessControlView):
    pass


class StlModelView(AccessControlView):
    can_create = False
    can_edit = True

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
