from flask import Blueprint, render_template, request, redirect, url_for
from app.models.categorias import Categoria
from app import db

# 🔹 Crear el Blueprint
categorias_bp = Blueprint('categorias', __name__, url_prefix='/categorias')

# 🔹 Listar categorías
@categorias_bp.route('/')
def listar_categorias():
    categorias = Categoria.query.all()
    return render_template('categorias/lista.html', categorias=categorias)

# 🔹 Agregar categoría
@categorias_bp.route('/agregar', methods=['POST'])
def agregar_categoria():
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    nueva_categoria = Categoria(nombre=nombre, descripcion=descripcion)
    db.session.add(nueva_categoria)
    db.session.commit()
    return redirect(url_for('categorias.listar_categorias'))

# 🔹 Eliminar categoría
@categorias_bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar_categoria(id):
    categoria = Categoria.query.get_or_404(id)
    db.session.delete(categoria)
    db.session.commit()
    return redirect(url_for('categorias.listar_categorias'))
