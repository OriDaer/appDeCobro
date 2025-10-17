from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, SelectField, FloatField, PasswordField
from wtforms.validators import DataRequired, Email, Length

class RegisterForm(FlaskForm):
    username = StringField("Usuario", validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = StringField("Contraseña", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Registrarse")

class LoginForm(FlaskForm):
    username = StringField("Usuario", validators=[DataRequired()])
    password = StringField("Contraseña", validators=[DataRequired()])
    submit = SubmitField("Ingresar")


