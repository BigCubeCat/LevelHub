import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class ResultAppreciated(SqlAlchemyBase):
    __tablename__ = 'result_appreciateds'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))  # Оценивший пользыватель
    result_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("results.id"))
    user = orm.relation('User')
    result = orm.relation("Result")
