from collections import OrderedDict
import yaml
import sqlalchemy as sa

from starship.data import db_session
from starship.data.detail_copy import DetailCopy
from .blueprint import admin_bp
from .helpers import admin_required, redirect_url, get_lang, yaml_to_sentence
from starship.data.sentence import Sentence
from starship.data.detail_type import DetailType
from starship.data.detail import Detail
from .forms.detail import DetailCreationForm, DetailTypeCreationForm

try:
    from yaml import CBaseLoader as YamlLoader
except ImportError:
    from yaml import BaseLoader as YamlLoader

from flask import flash, redirect, render_template, request, url_for


@admin_bp.route("/details")
@admin_required
def detail_management():
    db_sess = db_session.create_session()

    detail_types = db_sess.query(DetailType).order_by(DetailType.order).all()
    details = OrderedDict()
    for detail_type in detail_types:
        details[detail_type] = (
            db_sess.query(Detail)
            .filter_by(kind=detail_type)
            .order_by(Detail.cost)
            .all()
        )

    return render_template(
        "details.html",
        title="Detail Management",
        details_page=True,
        lang=get_lang(),
        detail_types=detail_types,
        details=details,
    )


@admin_bp.route("/create_detail_type", methods=["GET", "POST"])
@admin_required
def create_detail_type():
    form = DetailTypeCreationForm()

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        detail_type = DetailType()
        detail_type.name = yaml_to_sentence(form.name.data)
        detail_type.description = (
            yaml_to_sentence(form.description.data)
            if form.description.data
            else Sentence()
        )
        detail_type.required = form.required.data
        db_sess.add(detail_type)
        db_sess.commit()
        return redirect(url_for("admin_bp.detail_management"))

    return render_template(
        "create_detail_type.html",
        form=form,
        title="Detail Type creation",
        details_page=True,
    )


@admin_bp.route("/detail_type/<int:id>")
@admin_required
def detail_type(id):
    db_sess = db_session.create_session()
    dt = db_sess.query(DetailType).get(id)
    if not dt:
        flash(f"Detail type with id {id} not found")
        return redirect(redirect_url())
    return render_template(
        "detail_type.html",
        title=dt.name.en,
        lang=get_lang(),
        dt=dt,
        details_page=True,
    )


@admin_bp.route("/detail_type/<int:id>/change_order")
def change_detail_type_order(id):
    db_sess = db_session.create_session()

    dt = db_sess.query(DetailType).get(id)
    if not dt:
        flash(f"Detail type with id {id} not found")
        return redirect(redirect_url())

    dir = request.args.get("direction", None)

    if dir not in {"up", "down"}:
        flash("Direction to change order in was not specified")
        return redirect(redirect_url())

    if dir == "up":
        if not (
            dt_prev := db_sess.query(DetailType).filter_by(order=dt.order - 1).first()
        ):
            return redirect(redirect_url())
        dt.order -= 1
        dt_prev.order += 1
    elif dir == "down":
        if not (
            dt_next := db_sess.query(DetailType).filter_by(order=dt.order + 1).first()
        ):
            return redirect(redirect_url())
        dt.order += 1
        dt_next.order -= 1

    db_sess.commit()

    return redirect(redirect_url())


@admin_bp.route("/detail_type/<int:id>/edit", methods=["GET", "POST"])
@admin_required
def edit_detail_type(id):
    db_sess = db_session.create_session()
    dt = db_sess.query(DetailType).get(id)

    if not dt:
        flash(f"Detail type with id {id} not found")
        return redirect(redirect_url())

    form = DetailTypeCreationForm()

    if form.validate_on_submit():
        dt.name = yaml_to_sentence(form.name.data, dt.name)
        dt.description = (
            yaml_to_sentence(form.description.data, dt.description)
            if form.description.data
            else Sentence()
        )
        dt.required = form.required.data
        db_sess.commit()
        return redirect(url_for("admin_bp.detail_management"))

    return render_template(
        "edit_detail_type.html",
        title="Edit Detail Type",
        form=form,
        dt=dt,
        details_page=True,
    )


@admin_bp.route("/detail_type/<int:id>/delete")
@admin_required
def delete_detail_type(id):
    db_sess = db_session.create_session()
    dt = db_sess.query(DetailType).get(id)

    if not dt:
        flash(f"Detail type with id {id} not found")
        return redirect(redirect_url())

    try:
        db_sess.delete(dt)
        db_sess.delete(dt.name)
        db_sess.delete(dt.description)
        db_sess.commit()
    except sa.exc.SQLAlchemyError as e:
        flash(f"Error while deleting detail_type with id {id}: {e}")

    return redirect(url_for("admin_bp.detail_management"))


def apply_yaml_chars_on_detail(detail, chars):
    pyobj = yaml.load(chars, YamlLoader).items()

    for lang, value in pyobj:
        detail.__setattr__(lang, value)


@admin_bp.route("/create_detail", methods=["GET", "POST"])
@admin_required
def create_detail():
    db_sess = db_session.create_session()
    form = DetailCreationForm()
    lang = get_lang()

    form.kind.choices = [
        (dt.id, dt.name.__getattribute__(lang))
        for dt in db_sess.query(DetailType).all()
    ]

    if form.validate_on_submit():
        detail = Detail()
        detail.name = yaml_to_sentence(form.name.data)
        detail.description = (
            yaml_to_sentence(form.description.data)
            if form.description.data
            else Sentence()
        )
        detail.kind_id = form.kind.data
        detail.cost = form.cost.data
        detail.health = form.health.data
        apply_yaml_chars_on_detail(detail, form.chars.data)

        db_sess.add(detail)
        db_sess.commit()

        return redirect(url_for("admin_bp.detail_management"))

    return render_template(
        "create_detail.html",
        form=form,
        title="Detail creation",
        details_page=True,
    )


@admin_bp.route("/detail/<int:id>/edit", methods=["GET", "POST"])
@admin_required
def edit_detail(id):
    db_sess = db_session.create_session()
    detail = db_sess.query(Detail).get(id)

    if not detail:
        flash(f"Detail with id {id} not found")
        return redirect(redirect_url())

    form = DetailCreationForm()
    lang = get_lang()

    form.kind.choices = [
        (dt.id, dt.name.__getattribute__(lang))
        for dt in db_sess.query(DetailType).all()
    ]
    form.kind.data = detail.kind_id

    if form.validate_on_submit():
        detail.name = yaml_to_sentence(form.name.data, detail.name)
        detail.description = (
            yaml_to_sentence(form.description.data, detail.description)
            if form.description.data
            else Sentence()
        )
        detail.kind_id = form.kind.raw_data[0]
        detail.cost = form.cost.data
        detail.health = form.health.data
        apply_yaml_chars_on_detail(detail, form.chars.data)

        db_sess.commit()
        return redirect(url_for("admin_bp.detail_management", id=id))

    return render_template(
        "edit_detail.html",
        title="Edit Detail",
        form=form,
        detail=detail,
        details_page=True,
    )


@admin_bp.route("/detail/<int:id>/delete")
@admin_required
def delete_detail(id):
    db_sess = db_session.create_session()
    detail = db_sess.query(Detail).get(id)

    if not detail:
        flash(f"Detail with id {id} not found")
        return redirect(redirect_url())

    try:
        db_sess.delete(detail)
        db_sess.delete(detail.name)
        db_sess.delete(detail.description)
        db_sess.commit()
    except sa.exc.SQLAlchemyError as e:
        flash(f"Error while deleting detail_type with id {id}: {e}")

    return redirect(url_for("admin_bp.detail_management"))


@admin_bp.route("/detail_copy/<int:id>/repair")
@admin_required
def repair_detail_copy(id):
    db_sess = db_session.create_session()
    dc = db_sess.query(DetailCopy).get(id)

    if not dc:
        flash(f"Detail Copy with id {id} not found")
        return redirect(redirect_url())

    try:
        dc.health = dc.kind.health
        db_sess.commit()
    except sa.exc.DataError:
        flash(f'Failed to change currency to "{value}" cause of data processing issues')

    return redirect(redirect_url())


@admin_bp.route("/detail_copy/<int:id>/set_level/<value>")
@admin_required
def change_detail_copy_level(id, value):
    db_sess = db_session.create_session()
    dc = db_sess.query(DetailCopy).get(id)

    if not dc:
        flash(f"Detail Copy with id {id} not found")
        return redirect(redirect_url())

    try:
        dc.level = value
        db_sess.commit()
    except sa.exc.DataError:
        flash(f'Failed to change currency to "{value}" cause of data processing issues')

    return redirect(redirect_url())


@admin_bp.route("/detail_copy/<int:id>/delete")
@admin_required
def delete_detail_copy(id):
    db_sess = db_session.create_session()
    dc = db_sess.query(DetailCopy).get(id)

    if not dc:
        flash(f"Detail Copy with id {id} not found")
        return redirect(redirect_url())

    try:
        db_sess.delete(dc)
        db_sess.commit()
    except sa.exc.SQLAlchemyError as e:
        flash(f"Error while deleting detail_copy with id {id}: {e}")

    return redirect(url_for("admin_bp.detail_management"))
