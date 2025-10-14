from app import db
from datetime import datetime

class Movimiento(db.Model):
    __tablename__ = 'Movimientos'
    
    Id = db.Column(db.Integer, primary_key=True)
    ProductoId = db.Column(db.Integer, db.ForeignKey('Productos.Id'), nullable=False)
    Tipo = db.Column(db.String(20), nullable=False)
    Cantidad = db.Column(db.Numeric(10, 2), nullable=False)
    Motivo = db.Column(db.String(200), nullable=True)
    Notas = db.Column(db.Text, nullable=True)
    Usuario = db.Column(db.String(100), nullable=True)
    FechaCreacion = db.Column(db.DateTime, nullable=True)
    
    # Relación
    producto_rel = db.relationship('Producto', backref='movimientos_rel')
    
    def __repr__(self):
        return f'<Movimiento {self.Tipo} - {self.Cantidad} unidades>'