# appDeCobro
🛒 Simulador de Pago/Cobro con Flask y Mercado Pago

Este proyecto es una aplicación web desarrollada con **Python** y el framework **Flask** que simula un sistema de e-commerce básico con funcionalidades de gestión de productos, pedidos, registro/autenticación de usuarios y, crucialmente, la integración de un **Simulador de Pago/Cobro** utilizando la API de **Mercado Pago**.

---

🚀 Funcionalidades Principales

* **Autenticación de Usuarios:** Registro, inicio de sesión y cierre de sesión seguro implementado con **Flask-Login** y `werkzeug.security`.
* **Gestión de Productos:** Vistas para listar, agregar, editar y eliminar productos (solo listado y agregado implementado en el código base).
* **Carrito de Compras:** Sistema basado en **sesiones de Flask** para agregar y visualizar productos antes de la compra.
* **Sistema de Pedidos:** Creación y gestión de órdenes asociadas al usuario, con seguimiento de su estado.
* **Simulador de Pago/Cobro (Mercado Pago):** Integración con la SDK de Mercado Pago (`mercadopago`) para generar una preferencia de pago y simular la pasarela de cobro. El estado del pedido se actualiza a **'Pagado con MP'** tras la simulación exitosa.

---

🛠️ Tecnologías Utilizadas

* **Backend:** Python 3.x, Flask
* **Base de Datos:** SQLAlchemy (SQLite por defecto)
* **Autenticación:** Flask-Login, `werkzeug.security`
* **Formularios:** Flask-WTF
* **Integración de Pago:** SDK de Mercado Pago (`mercadopago`)
* **Configuración:** `python-dotenv` para gestión de variables de entorno (`.env`).
* **Modelos/Datos:** `flask_sqlalchemy` para la persistencia de datos.

---
⚙️ Configuración e Instalación

Sigue estos pasos para configurar y ejecutar el proyecto en tu máquina local.

 1. Clonar el Repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd <NOMBRE_DEL_PROYECTO>

 2. Crear Entorno Virtual(Recomendado)
 python3 -m venv venv
    source venv/bin/activate  # En Linux/macOS
    .\venv\Scripts\activate  # En Windows

3. Instalación de Dependencias
pip install -r requirements.txt
# Si no tienes requirements.txt, instala las principales:
 pip install Flask Flask-SQLAlchemy Flask-Login werkzeug Flask-WTF python-dotenv mercadopago pymysql Jinja2 Werkzeug WTForms

4. Configuración de Variables de Entorno
El proyecto requiere claves de entorno para la configuración de la aplicación y la integración con Mercado Pago.

Crea un archivo llamado .env en la raíz del proyecto y añade las siguientes variables:
 # fragmento del codigo 
 # Clave Secreta para la aplicación Flask
    SECRET_KEY="una_clave_secreta_fuerte_aqui"

    # Token de Acceso para la API de Mercado Pago (Necesitas una cuenta de desarrollador)
    # Utiliza un token de prueba para la simulación.
    MERCADOPAGO_ACCESS_TOKEN="TU_ACCESS_TOKEN_DE_MERCADO_PAGO"

    # URI de la base de datos (Ejemplo para SQLite)
    SQLALCHEMY_DATABASE_URI="sqlite:///site.db"

⚠️ Importante: Para obtener tu MERCADOPAGO_ACCESS_TOKEN, debes registrarte como desarrollador en Mercado Pago y generar credenciales de prueba. Este token es esencial para que la simulación de pago funcione.

5. Ejecutar la Aplicación
En tu terminal ejecuta python3 app.py y la aplicacion estará disponible en una url como: http://127.0.0.1:5000/


📝 Mini Documentación del Código
El archivo principal del proyecto es app.py, donde se encuentra la lógica central, la definición de modelos (aunque idealmente estarían en models.py) y las rutas (vistas).

--Estructura de Clases (Modelos)
    Las clases de modelo de datos están definidas dentro de app.py (o en models.py si se usa la estructura sugerida) usando db.Model de SQLAlchemy:

    User: Almacena información del usuario. Hereda de UserMixin para Flask-Login.

    username, email, password_hash.

    Product: Almacena los ítems disponibles.

    name, price, description.

    Order: Registra los pedidos realizados por los usuarios.

    user_id, date, total, status ('Pendiente', 'Pagado con MP').

--Flujo de Pago con Mercado Pago
    El usuario agrega productos al carrito (session['cart']).

    Al proceder al pago y hacer clic en el botón de MP, la ruta /create_mp_payment se ejecuta.

    Esta ruta utiliza la SDK de mercadopago para crear una preference con los ítems del carrito y las URLs de callback (success, failure, pending).

    El usuario es redireccionado al init_point de Mercado Pago para la simulación de pago.

    Tras simular el pago, MP redirige a una de las back_urls definidas:

    /mp_success: Crea una nueva Order en la base de datos con status='Pagado con MP', vacía el carrito de la sesión y notifica al usuario.

    /mp_failure o /mp_pending: Muestra el mensaje apropiado y devuelve al usuario al carrito.