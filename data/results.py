import sqlalchemy
from sqlalchemy import orm
import datetime
from .db_session import SqlAlchemyBase


class Result(SqlAlchemyBase):
    __tablename__ = 'results'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    karma = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    score = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                      default=datetime.datetime.now)
    author = sqlalchemy.Column(sqlalchemy.Integer,
                               sqlalchemy.ForeignKey("users.id"))
    level_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("levels.id"))
    user = orm.relation('User')
    level = orm.relation("Level")
