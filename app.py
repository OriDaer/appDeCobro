from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from config import Config
import mercadopago
from dotenv import load_dotenv
from forms import LoginForm, RegisterForm
from models import User, Product, Order

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

# Inicializar SQLAlchemy y Flask-Login
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- MODELOS ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(1024))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Pendiente')

# --- RUTAS ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('base.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('products'))
        flash('Usuario o contraseña incorrectos.')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('El usuario ya existe.')
            return redirect(url_for('register'))
        new_user = User(username=form.username.data, email=form.email.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Registro exitoso. Inicia sesión.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/products', methods=['GET', 'POST'])
@login_required
def products():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        product = Product(name=name, price=price, description=description)
        db.session.add(product)
        db.session.commit()
        flash('Producto agregado con éxito.')
    products = Product.query.all()
    return render_template('products.html', products=products)

@app.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    product_id = int(request.form['product_id'])
    quantity = int(request.form['quantity'])
    product = Product.query.get(product_id)
    if not product:
        flash('Producto no encontrado.')
        return redirect(url_for('products'))

    if 'cart' not in session:
        session['cart'] = []

    cart_item = {
        'product_id': product_id,
        'name': product.name,
        'price': product.price,
        'quantity': quantity
    }
    session['cart'].append(cart_item)
    session.modified = True
    flash(f"{product.name} agregado al carrito.")
    return redirect(url_for('products'))

@app.route('/cart')
@login_required
def view_cart():
    cart = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart)
    return render_template('cart.html', cart=cart, total=total)

@app.route('/create_order', methods=['POST'])
@login_required
def create_order():
    cart = session.get('cart', [])
    if not cart:
        flash('Tu carrito está vacío.')
        return redirect(url_for('view_cart'))

    total = sum(item['price'] * item['quantity'] for item in cart)
    order = Order(user_id=current_user.id, total=total)
    db.session.add(order)
    db.session.commit()
    session.pop('cart', None)
    flash('¡Orden creada con éxito!')
    return redirect(url_for('orders'))

@app.route('/create_mp_payment', methods=['POST'])
@login_required
def create_mp_payment():
    cart = session.get('cart', [])
    if not cart:
        flash('Tu carrito está vacío.')
        return redirect(url_for('view_cart'))

    sdk = mercadopago.SDK(str(app.config["MERCADOPAGO_ACCESS_TOKEN"]))

    items = []
    for item in cart:
        items.append({
            "title": item['name'],
            "unit_price": float(item['price']),
            "quantity": item['quantity'],
        })

    preference_data = {
        "items": items,
        "back_urls": {
            "success": url_for('mp_success', _external=True),
            "failure": url_for('mp_failure', _external=True),
            "pending": url_for('mp_pending', _external=True),
        },
        #"auto_return": "approved",
    }

    # Crear preferencia
    preference_response = sdk.preference().create(preference_data)
    print("DEBUG: preference_response:", preference_response)  # 🔹 VER qué devuelve
    preference = preference_response.get("response", {})

    # Revisar si hay 'id'
    preference_id = preference.get('id')
    if not preference_id:
        flash("Hubo un problema creando la preferencia de pago. Revisa la consola.")
        return redirect(url_for('view_cart'))

    # Todo ok, guardamos en session
    session['preference_id'] = preference_id
    return redirect(preference.get('init_point', url_for('view_cart')))
@app.route('/mp_success')
@login_required
def mp_success():
    cart = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart)
    order = Order(user_id=current_user.id, total=total, status='Pagado con MP')
    db.session.add(order)
    db.session.commit()
    session.pop('cart', None)
    session.pop('preference_id', None)
    flash('¡Pago exitoso! Tu orden ha sido creada.')
    return redirect(url_for('orders'))

@app.route('/mp_failure')
@login_required
def mp_failure():
    flash('El pago no pudo ser procesado.')
    return redirect(url_for('view_cart'))

@app.route('/mp_pending')
@login_required
def mp_pending():
    flash('El pago está en proceso. Te notificaremos cuando se confirme.')
    return redirect(url_for('view_cart'))

@app.route('/orders')
@login_required
def orders():
    orders = Order.query.filter_by(user_id=current_user.id).all()
    products = Product.query.all()
    return render_template('orders.html', orders=orders, products=products)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# --- CREAR TABLAS ---
with app.app_context():
    # Crear un contexto de conexión
    with db.engine.connect() as conn:
        conn.execute(
            db.text("ALTER TABLE user MODIFY password_hash VARCHAR(1024)")
        )
        conn.commit()  # confirmar cambios

    # Crear tablas si no existen
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)