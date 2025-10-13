from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.categorias import Categoria
from app import db
from datetime import datetime

categorias_bp = Blueprint('categorias', __name__, url_prefix='/categorias')

# Listar categorías
@categorias_bp.route('/')
def listar_categorias():
    categorias = Categoria.query.all()
    return render_template('categorias/lista.html', categorias=categorias)

# Agregar categoría
@categorias_bp.route('/agregar', methods=['POST'])
def agregar_categoria():
    nombre = request.form['nombre'].strip()
    descripcion = request.form.get('descripcion', '').strip()
    fecha_creacion_str = request.form.get("fechaCreacion")
    
    fecha_creacion = datetime.strptime(fecha_creacion_str, '%Y-%m-%d %H:%M:%S')

    if not nombre:
        flash('El nombre es obligatorio.', 'danger')
        return redirect(url_for('categorias.listar_categorias'))

    existente = Categoria.query.filter_by(Nombre=nombre).first()
    if existente:
        flash('Ya existe una categoría con ese nombre.', 'warning')
        return redirect(url_for('categorias.listar_categorias'))

    nueva_categoria = Categoria(Nombre=nombre, Descripcion=descripcion,FechaCreacion=fecha_creacion)
    db.session.add(nueva_categoria)
    db.session.commit()
    flash('Categoría creada correctamente.', 'success')
    return redirect(url_for('categorias.listar_categorias'))

# Editar categoría
@categorias_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_categoria(id):
    categoria = Categoria.query.get_or_404(id)

    if request.method == 'POST':
        nombre = request.form['nombre'].strip()
        descripcion = request.form.get('descripcion', '').strip()

        if not nombre:
            flash('El nombre no puede estar vacío.', 'danger')
            return redirect(url_for('categorias.editar_categoria', id=id))

        existente = Categoria.query.filter(Categoria.Nombre == nombre, Categoria.Id != id).first()
        if existente:
            flash('Ya existe otra categoría con ese nombre.', 'warning')
            return redirect(url_for('categorias.editar_categoria', id=id))

        categoria.Nombre = nombre
        categoria.Descripcion = descripcion
        db.session.commit()
        flash('Categoría actualizada correctamente.', 'success')
        return redirect(url_for('categorias.listar_categorias'))

    return render_template('categorias/editar.html', categoria=categoria)

# Eliminar categoría
@categorias_bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar_categoria(id):
    categoria = Categoria.query.get_or_404(id)

    db.session.delete(categoria)
    db.session.commit()
    flash('Categoría eliminada correctamente.', 'success')
    return redirect(url_for('categorias.listar_categorias'))

