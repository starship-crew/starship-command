import sqlalchemy as sa

from typing import List
from collections import OrderedDict
from starship.data.detail_copy import DetailCopy

from starship.data.detail_type import DetailType
from starship.helpers import get_ordered_detail_copies

from . import db
from .db import SqlAlchemyBase


class Garage(SqlAlchemyBase):
    __tablename__ = "garages"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)

    crew_id = sa.Column(sa.Integer, sa.ForeignKey("crews.id"))
    crew = sa.orm.relationship("Crew", back_populates="garage", foreign_keys=[crew_id])

    details: sa.orm.Mapped[List["DetailCopy"]] = sa.orm.relationship(
        back_populates="garage"
    )

    def __repr__(self):
        return f"Garage(id={self.id!r}, details={self.details})"

    def ordered_details(self, db_sess) -> OrderedDict[DetailType, DetailCopy]:
        return get_ordered_detail_copies(
            db_sess, lambda q, dt: q.filter(DetailCopy.garage == self)
        )

    def as_response(self, db_sess):
        return {
            "detail_types": [
                dt.as_response for dt in self.ordered_details(db_sess).keys()
            ],
            "detail_copies": {
                dt.id: [detail.as_response for detail in details]
                for dt, details in self.ordered_details(db_sess).items()
            },
        }
