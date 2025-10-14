from app import db
from datetime import datetime

class Producto(db.Model):
    __tablename__ = 'Productos'
    
    Id = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(150), nullable=False)
    Descripcion = db.Column(db.Text)
    CodigoSKU = db.Column(db.String(50), unique=True, nullable=False)
    CantidadActual = db.Column(db.Integer, default=0)
    UnidadMedida = db.Column(db.String(20), nullable=False)
    StockMinimo = db.Column(db.Integer, default=0)
    PrecioUnitario = db.Column(db.Numeric(10, 2), nullable=False)
    CategoriaId = db.Column(db.Integer, db.ForeignKey('Categorias.Id'))
    ProveedorId = db.Column(db.Integer, db.ForeignKey('Proveedores.Id'))
    Activo = db.Column(db.Boolean, default=True)
    FechaCreacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    categoria = db.relationship('Categoria', backref='productos')
    proveedor = db.relationship('Proveedor', backref='productos')
    
    def estado_stock(self):
        """Determina el estado del stock según RF-010"""
        if self.CantidadActual == 0:
            return 'critico'
        elif self.CantidadActual <= self.StockMinimo:
            return 'bajo'
        else:
            return 'normal'
    
    def __repr__(self):
        return f'<Producto {self.Nombre}>'