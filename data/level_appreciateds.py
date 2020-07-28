import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class LevelAppreciated(SqlAlchemyBase):
    __tablename__ = 'level_appreciateds'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))  # Оценивший пользыватель
    level_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("levels.id"))
    user = orm.relation('User')
    level = orm.relation("Level")
