from flask import Blueprint, current_app, g, make_response, redirect, render_template, request, url_for

import uuid

from print3dstore.wrapper_functions import error_handler
from print3dstore.errors import RequestException
from print3dstore.blueprints.auth import login_required
from print3dstore.models import PaymentGateway, Spool, User, db, File, Material, Order, StlModel

from .forms.order import OrderForm

from .tasks import tasks

bp = Blueprint("order", __name__)

@bp.route("/order", methods=["GET", "POST"])
@error_handler
@login_required
def order():
    materials = db.session.scalars(db.select(Material)).all()
    spools = db.session.scalars(db.select(Spool)).all()
    payment_gateways = db.session.scalars(db.select(PaymentGateway)).all()
    form = OrderForm()
    form.material.choices = list(
        map(
            lambda material: material.name,
            materials
        )
    )
    form.color.choices = list(
        map(
            lambda spool: spool.color,
            spools
        )
    )
    form.payment_method.choices = list(
        map(
            lambda payment_gateway: payment_gateway.name,
            payment_gateways
        )
    )
    if request.method == "POST":
        form.process(request.form)
        form.stl_models.raw_data = request.files.getlist("stl_models")
        if not form.validate():
            return render_template("order.html", form=form)

        stl_files = request.files.getlist("stl_models")
        material = request.form.get("material")
        color = request.form.get("color")
        city = request.form.get("city")
        address_line1 = request.form.get("address_line1")
        address_line2 = request.form.get("address_line2")
        phone = request.form.get("phone")
        payment_method = request.form.get("payment_method")

        material = db.first_or_404(
            db.select(Material).filter_by(name=material),
            description=f"No such material found in our database"
        )

        user = db.get_or_404(
            User, g.user.id
        )

        user.address_line1 = address_line1
        user.address_line2 = address_line2
        user.city = city
        user.phone = phone

        payment_gateway = db.first_or_404(
            db.select(PaymentGateway).filter_by(name=payment_method)
        )

        files_added = []
        for stl_file in stl_files:
            file_path = f"{current_app.root_path}/media/{material.name}-{color}-{str(uuid.uuid4())}-{stl_file.filename}"
            tasks.slice.delay(file_path)
            stl_file.save(file_path)
            new_file = File(full_path=file_path)

            db.session.add(new_file)
            files_added.append(new_file)

        stl_models = []
        for file in files_added:
            stl_model = StlModel(file=file, color=color)
            stl_model.material = material

            db.session.add(stl_model)
            stl_models.append(stl_model)

        order = Order(
            user=g.user,
            stl_models=stl_models,
            payment_gateway=payment_gateway,
        )

        db.session.add(order)

        db.session.commit()

        return redirect(url_for("main.root"))
    
    return render_template("order.html", form=form)

