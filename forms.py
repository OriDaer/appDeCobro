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

class ProductoForm(FlaskForm):
    name = StringField("Nombre", validators=[DataRequired()])
    price = FloatField("Precio", validators=[DataRequired()])
    description = StringField("Descripción")
    submit = SubmitField("Agregar Producto")

class PedidoForm(FlaskForm):
    producto_id = IntegerField("ID Producto", validators=[DataRequired()])
    cantidad = IntegerField("Cantidad", validators=[DataRequired()])
    submit = SubmitField("Crear Pedido")

class PagoForm(FlaskForm):
    metodo = SelectField("Método de Pago", choices=[
        ("efectivo", "Efectivo"),
        ("tarjeta", "Tarjeta"),
        ("transferencia", "Transferencia")
    ], validators=[DataRequired()])
    monto = FloatField("Monto", validators=[DataRequired()])
    submit = SubmitField("Confirmar Pago")
