import sqlalchemy as sa

from starship import api
from flask import flash, redirect, request
from starship.data.crew import Crew
from starship.data import db_session
from starship.data.user import User
from .blueprint import admin_bp
from .helpers import admin_required, redirect_url


@admin_bp.route("/create_crew/<name>")
@admin_required
def create_crew(name):
    api.create_crew(name)
    return redirect(redirect_url())


@admin_bp.route("/crew/<int:id>/link")
@admin_required
def link_crew(id):
    db_sess = db_session.create_session()
    crew = db_sess.query(Crew).get(id)

    if not crew:
        flash(f"Crew with id {id} not found")
        return redirect(redirect_url())

    if user_ids := request.args.get("users", None):
        try:
            user_ids = set(map(int, user_ids.split(",")))
        except ValueError:
            flash(
                f"Could not convert provided user identifiers ({user_ids}) to integers to link crew {id} with them"
            )
            return redirect(redirect_url())
        for user in db_sess.query(User).filter(User.id.in_(user_ids)):
            crew.owners.add(user)
        db_sess.commit()

    return redirect(redirect_url())


@admin_bp.route("/crew/<int:id>/unlink")
@admin_required
def unlink_crew(id):
    db_sess = db_session.create_session()
    crew = db_sess.query(Crew).get(id)

    if not crew:
        flash(f"Crew with id {id} not found")
        return redirect(redirect_url())

    if user_ids := request.args.get("users", None):
        try:
            user_ids = set(map(int, user_ids.split(",")))
        except ValueError:
            flash(
                f"Could not convert provided user identifiers ({user_ids}) to integers to unlink crew {id} with them"
            )
            return redirect(redirect_url())
        for user in db_sess.query(User).filter(User.id.in_(user_ids)):
            crew.owners.remove(user)
        db_sess.commit()

    return redirect(redirect_url())


@admin_bp.route("/crew/<int:id>/delete")
@admin_required
def delete_crew(id):
    db_sess = db_session.create_session()
    crew = db_sess.query(Crew).get(id)

    if not crew:
        flash(f"Crew with id {id} not found")
        return redirect(redirect_url())

    try:
        db_sess.delete(crew)
        db_sess.commit()
    except sa.exc.SQLAlchemyError as e:
        flash(f"Error while deleting crew with id {id}: {e}")

    return redirect(redirect_url())
