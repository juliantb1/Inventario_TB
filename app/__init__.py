from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = (
        'mssql+pyodbc://@localhost/InventarioRestaurante?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'clave-secreta'

    db.init_app(app)

    # Ruta de inicio CON DASHBOARD
    @app.route('/')
    def inicio():
        # Importar modelos aquí para evitar importaciones circulares
        from app.models.productos import Producto
        from app.models.movimientos import Movimiento
        
        try:
            # KPIs principales
            total_productos = Producto.query.filter_by(Activo=True).count()
            
            productos_bajo_stock = Producto.query.filter(
                Producto.CantidadActual <= Producto.StockMinimo,
                Producto.Activo == True
            ).count()
            
            productos_sin_stock = Producto.query.filter(
                Producto.CantidadActual == 0,
                Producto.Activo == True
            ).count()
            
            # Calcular valor total del inventario
            productos = Producto.query.filter_by(Activo=True).all()
            valor_total = sum(producto.CantidadActual * float(producto.PrecioUnitario) for producto in productos)
            
            # Widget: Productos bajo stock (máximo 10)
            productos_bajo_stock_lista = Producto.query.filter(
                Producto.CantidadActual <= Producto.StockMinimo,
                Producto.Activo == True
            ).order_by(Producto.CantidadActual.asc()).limit(10).all()
            
            # Widget: Últimos movimientos (últimos 5)
            ultimos_movimientos = Movimiento.query.order_by(Movimiento.FechaCreacion.desc()).limit(5).all()
            
            return render_template('inicio.html', 
                                 kpis={
                                     'total_productos': total_productos,
                                     'productos_bajo_stock': productos_bajo_stock,
                                     'productos_sin_stock': productos_sin_stock,
                                     'valor_total_inventario': f"{valor_total:,.2f}"
                                 },
                                 productos_bajo_stock=productos_bajo_stock_lista,
                                 ultimos_movimientos=ultimos_movimientos,
                                 fecha_actual=datetime.now().strftime('%d/%m/%Y %H:%M'))
        
        except Exception as e:
            # En caso de error, mostrar dashboard vacío
            print(f"Error cargando dashboard: {e}")
            return render_template('inicio.html', 
                                 kpis={
                                     'total_productos': 0,
                                     'productos_bajo_stock': 0,
                                     'productos_sin_stock': 0,
                                     'valor_total_inventario': "0.00"
                                 },
                                 productos_bajo_stock=[],
                                 ultimos_movimientos=[],
                                 fecha_actual=datetime.now().strftime('%d/%m/%Y %H:%M'))

    # Importar y registrar blueprints
    from app.routes.categorias import categorias_bp
    from app.routes.proveedores import proveedores_bp
    from app.routes.productos import productos_bp
    from app.routes.movimientos import movimientos_bp
    
    app.register_blueprint(categorias_bp)
    app.register_blueprint(proveedores_bp)
    app.register_blueprint(productos_bp)
    app.register_blueprint(movimientos_bp)

    with app.app_context():
        # Importar modelos para que SQLAlchemy los reconozca
        from app.models.categorias import Categoria
        from app.models.proveedores import Proveedor
        from app.models.productos import Producto
        from app.models.movimientos import Movimiento
        
        # Crear todas las tablas
        db.create_all()

    return app