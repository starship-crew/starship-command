import sqlalchemy as sa

from .db_session import SqlAlchemyBase


garage_groups = sa.Table(
    "garage_groups",
    SqlAlchemyBase.metadata,
    sa.Column("garage_id", sa.ForeignKey("garages.id")),
    sa.Column("detail_id", sa.ForeignKey("details_copies.id")),
)