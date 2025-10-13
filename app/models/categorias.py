from app import db
from datetime import datetime

class Categoria(db.Model):
    __tablename__ = 'Categorias'

    Id = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(100), nullable=False, unique=True)
    Descripcion = db.Column(db.String(200))
    Activo = db.Column(db.Boolean, default=True)     
    FechaCreacion = db.Column(db.DateTime, nullable=False)
    
    def __repr__(self):
        return f'<Categoria {self.Nombre}>'