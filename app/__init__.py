from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = (
        'mssql+pyodbc://@localhost/InventarioRestaurante?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'clave-secreta'

    db.init_app(app)

    # Ruta de inicio
    @app.route('/')
    def inicio():
        return render_template('inicio.html')

    # Importar y registrar blueprints
    from app.routes.categorias import categorias_bp
    from app.routes.proveedores import proveedores_bp
    from app.routes.productos import productos_bp  # NUEVO
    
    app.register_blueprint(categorias_bp)
    app.register_blueprint(proveedores_bp)
    app.register_blueprint(productos_bp)  # NUEVO

    with app.app_context():
        # Importar modelos para que SQLAlchemy los reconozca
        from app.models.categorias import Categoria
        from app.models.proveedores import Proveedor
        from app.models.productos import Producto  # NUEVO
        
        # Crear todas las tablas
        db.create_all()

    return app