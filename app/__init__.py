from flask import Flask
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

    
    from app.routes.categorias import categorias_bp
    app.register_blueprint(categorias_bp)

    with app.app_context():
        from app.models.categorias import Categoria
        
        pass

    return app

