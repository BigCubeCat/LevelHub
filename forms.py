from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField, IntegerField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from validators import PasswordValidator, NickValidator, ResultIDValidator


class RegisterForm(FlaskForm):
    """Форма Регистрации"""
    email = EmailField('Login/email', validators=[DataRequired()])
    nick = StringField('Nick', validators=[DataRequired(), NickValidator()])
    password = PasswordField('Password', validators=[DataRequired(), PasswordValidator()])
    password_again = PasswordField('Repeat password',
                                   validators=[DataRequired(), PasswordValidator()])
    remember_me = BooleanField("Remember me")
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    """Форма авторизации"""
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField("Remember me")
    submit = SubmitField('Login')


class ChangePasswordForm(FlaskForm):
    """Форма смены пароля"""
    password = PasswordField('Password', validators=[DataRequired(), PasswordValidator()])
    password_again = PasswordField('Repeat password',
                                   validators=[DataRequired(), PasswordValidator()])
    submit = SubmitField("Save")


class ChangeNickForm(FlaskForm):
    nick = StringField("Nick", validators=[DataRequired(), NickValidator()])
    submit = StringField("Save")


class LevelForm(FlaskForm):
    """Форма создвния уровня"""
    title = StringField("Title", validators=[DataRequired()])
    is_private = BooleanField("Is Private")
    hard = IntegerField("Hard Level", validators=[DataRequired()])
    content = FileField("Level Source", validators=[
        DataRequired(),
        FileAllowed(["level", "txt"], "Only .level Files")
    ])
    submit = SubmitField("Public Level")


class ResultForm(FlaskForm):
    """Форма создания результата для уровня"""
    level = IntegerField("Level ID", validators=[DataRequired(), ResultIDValidator()])
    content = FileField("Result File", validators=[
        DataRequired(), FileAllowed(["result", "txt"],
                                    "Only .result Files")])
    comment = StringField("Your Comment")
    submit = SubmitField("Public Result")


class MazeGeneratorForm(FlaskForm):
    """Форма для задания параметров генерируемого лабиринта"""
    width = IntegerField(validators=[DataRequired()])
    height = IntegerField(validators=[DataRequired()])
    submit = SubmitField("Generate Maze")
