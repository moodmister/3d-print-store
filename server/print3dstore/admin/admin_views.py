import datetime
import json
import math
import os
from flask import app, flash, g, make_response, redirect, render_template, request, session
from werkzeug.security import generate_password_hash
from flask_admin import BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm, rules
from wtforms.validators import DataRequired

from print3dstore.models import Material, PaymentGateway, StlModel, User, UserRole, db, Order, Role, Spool
from print3dstore.errors import RequestException
from print3dstore.blueprints.forms.order import OrderEditForm
from print3dstore.blueprints.forms.user import UserForm

class DashboardView(AdminIndexView):

    def is_visible(self):
        # This view won't appear in the menu structure
        return False

    @expose('/')
    def index(self):

        return redirect("/admin/analytics")


class AnalyticsView(BaseView):
    @expose("/")
    def index(self):
        spools = db.session.scalars(db.select(Spool)).all()
        orders = db.session.scalars(db.select(Order)).all()
        return self.render('admin/analytics.html', spools=spools, orders=orders)
    
    def is_accessible(self):
        if g.user is None:
            return False
        return g.user.has_permission(Role.all_permissions["Spool"]["read"]) or g.user.has_permission(Role.all_permissions["Superuser"])

class AccessControlView(ModelView):
    form_base_class = SecureForm
    can_set_page_size = True

    def is_accessible(self):
        if g.user is None:
            return False
        return g.user.has_permission(Role.all_permissions[self.name]["read"]) or g.user.has_permission(Role.all_permissions["Superuser"])


class UserView(AccessControlView):
    can_create = False
    column_list = [
        "id",
        "first_name",
        "last_name",
        "email",
        "roles",
        "city",
        "postal_code",
        "address_line1",
        "address_line2",
        "phone",
    ]
    column_searchable_list = ["first_name", "last_name", "email"]

    column_formatters = dict(
        roles=lambda _v, _c, m, _p: ", ".join(list(map(lambda user_role: user_role.role.name ,m.roles)))
    )

    form = UserForm

    @expose("/edit", methods=["GET", "POST"])
    def edit_view(self):
        if request.method == "GET":
            return super().edit_view()
        roles = db.session.scalars(db.select(Role)).all()

        user_form = UserForm()
        user_form.roles.choices = [(role.id, role.name) for role in roles]
        user_form.process(request.form)

        if not user_form.validate():
            flash(user_form.errors)
            return redirect("/admin/users")

        user = db.get_or_404(User, request.args["id"])
        other_users = db.session.scalars(db.select(User).where(User.id != user.id)).all()

        for other_user in other_users:
            if other_user.email == user_form.email.data:
                flash("Email already exists", "danger")
                return redirect("/admin/users")

        if user_form.email.data != user.email:
            print(user_form.email.data, user.email)
            user.email = user_form.email.data

        if user_form.password.data not in (None, ""):
            user.password = generate_password_hash(user_form.password.data)

        for role in user.roles:
            db.session.delete(role)
        for role_id in user_form.roles.data:
            user_role = UserRole(user_id=user.id, role_id=int(role_id))
            db.session.add(user_role)

        user.first_name = user_form.first_name.data
        user.last_name = user_form.last_name.data
        user.city = user_form.city.data
        user.postal_code = user_form.postal_code.data
        user.address_line1 = user_form.address_line1.data
        user.address_line2 = user_form.address_line2.data
        user.phone = user_form.phone.data

        db.session.commit()

        return redirect("/admin/users")


    def on_form_prefill(self, form, id):
        user = db.get_or_404(User, id)
        roles = db.session.scalars(db.select(Role)).all()
        form.roles.choices = [(role.id, role.name) for role in roles]
        form.roles.process_data([(user_role.role.id) for user_role in user.roles])

        return super().on_form_prefill(form, id)

    def on_model_delete(self, model):
        if g.user.id == model.id:
            session.clear()
        return super().on_model_delete(model)


class OrderView(AccessControlView):
    column_filters = ["user", "status"]
    can_create = False
    form = OrderEditForm
    column_list = [
        "order_id",
        "user",
        "stl_models",
        "estimated_cost",
        "estimated_printing_time",
        "payment_gateway",
        "address",
        "status",
    ]
    column_sortable_list = (
        ("user", ("user.email")),
        ("payment_gateway", ("payment_gateway.type")),
        "status",
    )
    column_searchable_list = (
        "id",
        "user.email",
        "city",
        "address_line1",
        "address_line2",
        "status"
    )
    column_formatters = dict(
        order_id=lambda  _v, _c, m, _p: f"#{m.id}",
        user=lambda _v, _c, m, _p: m.user.email,
        stl_models=lambda _v, _c, m, _p: list(
            map(
                lambda model: model.file.full_path[
                    model.file.full_path.rfind("/") + 1:
                ],
                m.stl_models
            )
        ),
        estimated_cost=lambda _v, _c, m, _p: f"""BGN {math.fsum(list(
            map(
                lambda model: model.estimated_cost / 100.0 if model.estimated_cost else 0,
                m.stl_models
            )
        ))} lv.""",
        estimated_printing_time=lambda _v, _c, m, _p: math.fsum(map(
            lambda model: math.ceil(model.estimated_time / 3600) if model.estimated_time else 0,
            m.stl_models
        )),
        payment_gateway=lambda _v, _c, m, _p: m.payment_gateway.type,
        address=lambda _v, _c, m, _p: f"{m.city}, {m.address_line1}, {m.address_line2}"
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

        form.city.data = order.city
        form.postal_code.data = order.postal_code
        form.address_line1.data = order.address_line1
        form.address_line2.data = order.address_line2
        form.phone.data = order.phone

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

            order.city = request.form.get("city")
            order.postal_code = request.form.get("postal_code")
            order.phone = request.form.get("phone")
            order.address_line1 = request.form.get("address_line1")
            order.address_line2 = request.form.get("address_line2")
            
            order.payment_gateway_id = request.form.get("payment_method")
            order.status = request.form.get("status")

            db.session.commit()

            return redirect("/admin/orders/")
        return super().edit_view()
    
    @expose("/delete", methods=["POST"])
    def delete_view(self):
        order = db.get_or_404(Order, request.form["id"])
        files = [stl_model.file for stl_model in order.stl_models]
        for file in files:
            db.session.delete(file)
        db.session.commit()
        try:
            for stl_model in order.stl_models:
                os.remove(stl_model.file.full_path)
                os.remove(stl_model.file.full_path.replace(".stl", ".gcode"))
        except OSError as e:
            pass
        return super().delete_view()


class MaterialView(AccessControlView):
    column_list = [
        "name",
        "cost_per_gram",
    ]
    column_formatters = {
        "cost_per_gram": lambda _v, _c, m, _p: m.cost_per_gram / 100.0,
    }
    form_columns = [
        "name",
        "cost_per_gram"
    ]
    form_args = {
        "cost_per_gram": {"label": "Cost per gram (in cents)", "validators": [DataRequired()]}
    }
    @expose("/delete", methods=["POST"])
    def delete_view(self):
        material = db.get_or_404(Material, request.form["id"])
        spools = db.session.scalars(db.select(Spool).filter(Spool.material_id == material.id)).all()
        stl_models = db.session.scalars(db.select(StlModel).filter(StlModel.material_id == material.id)).all()
        if len(spools) > 0 or len (stl_models):
            flash(f"Material {material.name} is used in stl models or spools. Delete them first.")
            return redirect("/admin/materials")

        return super().delete_view()


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
        estimated_cost=lambda _v, _c, m, _p: f"BGN {m.estimated_cost / 100.0} lv." if m.estimated_cost else 0,
        estimated_time=lambda _v, _c, m, _p: str(datetime.timedelta(seconds=m.estimated_time)) if m.estimated_time else 0
    )

class RoleView(AccessControlView):
    column_list = [
        "name",
        "permissions",
    ]
    column_formatters = dict(
        permissions=lambda _v, _c, m, _p: ", ".join(
            str(perm) for perm in json.loads(m.permissions)
        )
    )
    form_columns = [
        "name",
        "permissions"
    ]
    @expose("/delete", methods=["POST"])
    def delete_view(self):
        role = db.get_or_404(Role, request.form["id"])
        if len(role.users) > 0:
            flash(f"Role {role.name} has users assigned to it. It cannot be deleted.", "danger")
            return redirect("/admin/roles")
        return super().delete_view()
