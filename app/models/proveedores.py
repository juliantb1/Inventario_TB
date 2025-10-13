from app import db
from datetime import datetime

class Proveedor(db.Model):
    __tablename__ = 'Proveedores'
    
    Id = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(150), nullable=False)
    Contacto = db.Column(db.String(100))
    Telefono = db.Column(db.String(20))
    Email = db.Column(db.String(150))
    Direccion = db.Column(db.Text)
    Activo = db.Column(db.Boolean, default=True)
    FechaCreacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Proveedor {self.Nombre}>'