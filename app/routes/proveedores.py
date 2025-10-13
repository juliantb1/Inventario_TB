from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.proveedores import Proveedor
from app import db
import re

proveedores_bp = Blueprint('proveedores', __name__, url_prefix='/proveedores')

def validar_email(email):
    if not email:
        return True
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, email) is not None

# RF-005: Crear Proveedor
@proveedores_bp.route('/crear', methods=['GET', 'POST'])
def crear_proveedor():
    if request.method == 'POST':
        nombre = request.form['nombre'].strip()
        contacto = request.form.get('contacto', '').strip()
        telefono = request.form.get('telefono', '').strip()
        email = request.form.get('email', '').strip().lower()
        direccion = request.form.get('direccion', '').strip()
        
        # Validaciones RF-005
        if not nombre:
            flash('El nombre es obligatorio.', 'danger')
            return render_template('proveedores/crear.html')
        
        if len(nombre) > 150:
            flash('El nombre no puede exceder los 150 caracteres.', 'danger')
            return render_template('proveedores/crear.html')
        
        if contacto and len(contacto) > 100:
            flash('El contacto no puede exceder los 100 caracteres.', 'danger')
            return render_template('proveedores/crear.html')
        
        if telefono and len(telefono) > 20:
            flash('El telefono no puede exceder los 20 caracteres.', 'danger')
            return render_template('proveedores/crear.html')
        
        if email and not validar_email(email):
            flash('El formato del email no es valido.', 'danger')
            return render_template('proveedores/crear.html')
        
        # Verificar si ya existe
        existente = Proveedor.query.filter_by(Nombre=nombre).first()
        if existente:
            flash('Ya existe un proveedor con ese nombre.', 'warning')
            return render_template('proveedores/crear.html')
        
        # Crear proveedor
        nuevo_proveedor = Proveedor(
            Nombre=nombre,
            Contacto=contacto,
            Telefono=telefono,
            Email=email,
            Direccion=direccion
        )
        
        db.session.add(nuevo_proveedor)
        db.session.commit()
        
        flash('Proveedor creado exitosamente.', 'success')
        return redirect(url_for('proveedores.listar_proveedores'))
    
    return render_template('proveedores/crear.html')

# RF-006: Listar Proveedores
@proveedores_bp.route('/')
def listar_proveedores():
    search = request.args.get('search', '')
    estado = request.args.get('estado', '')
    
    query = Proveedor.query
    
    if search:
        query = query.filter(Proveedor.Nombre.ilike(f'%{search}%'))
    
    if estado:
        if estado == 'activo':
            query = query.filter(Proveedor.Activo == True)  # CAMBIADO: Estado -> Activo
        elif estado == 'inactivo':
            query = query.filter(Proveedor.Activo == False)  # CAMBIADO: Estado -> Activo
    
    proveedores = query.order_by(Proveedor.Nombre.asc()).all()
    return render_template('proveedores/lista.html', proveedores=proveedores)

# RF-007: Editar Proveedor
@proveedores_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)
    
    if request.method == 'POST':
        nombre = request.form['nombre'].strip()
        contacto = request.form.get('contacto', '').strip()
        telefono = request.form.get('telefono', '').strip()
        email = request.form.get('email', '').strip().lower()
        direccion = request.form.get('direccion', '').strip()
        
        # Validaciones RF-007 (mismas que RF-005)
        if not nombre:
            flash('El nombre es obligatorio.', 'danger')
            return render_template('proveedores/editar.html', proveedor=proveedor)
        
        if len(nombre) > 150:
            flash('El nombre no puede exceder los 150 caracteres.', 'danger')
            return render_template('proveedores/editar.html', proveedor=proveedor)
        
        if contacto and len(contacto) > 100:
            flash('El contacto no puede exceder los 100 caracteres.', 'danger')
            return render_template('proveedores/editar.html', proveedor=proveedor)
        
        if telefono and len(telefono) > 20:
            flash('El telefono no puede exceder los 20 caracteres.', 'danger')
            return render_template('proveedores/editar.html', proveedor=proveedor)
        
        if email and not validar_email(email):
            flash('El formato del email no es valido.', 'danger')
            return render_template('proveedores/editar.html', proveedor=proveedor)
        
        # Verificar si ya existe (excluyendo el actual)
        existente = Proveedor.query.filter(
            Proveedor.Nombre == nombre, 
            Proveedor.Id != id
        ).first()
        if existente:
            flash('Ya existe otro proveedor con ese nombre.', 'warning')
            return render_template('proveedores/editar.html', proveedor=proveedor)
        
        # Actualizar proveedor
        proveedor.Nombre = nombre
        proveedor.Contacto = contacto
        proveedor.Telefono = telefono
        proveedor.Email = email
        proveedor.Direccion = direccion
        
        db.session.commit()
        flash('Proveedor actualizado exitosamente.', 'success')
        return redirect(url_for('proveedores.listar_proveedores'))
    
    return render_template('proveedores/editar.html', proveedor=proveedor)

# RF-008: Eliminar/Desactivar Proveedor
@proveedores_bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)
    
    # RF-008: Advertir si tiene productos asociados
    # (Aquí necesitarías la relación con Productos cuando la crees)
    # tiene_productos = len(proveedor.productos) > 0 if proveedor.productos else False
    # if tiene_productos:
    #     flash('Advertencia: Este proveedor tiene productos asociados. Se desactivara de todas formas.', 'warning')
    
    # Desactivar proveedor (eliminacion logica)
    proveedor.Activo = False  # CAMBIADO: Estado -> Activo
    db.session.commit()
    
    flash('Proveedor desactivado exitosamente.', 'success')
    return redirect(url_for('proveedores.listar_proveedores'))

# Reactivar Proveedor
@proveedores_bp.route('/reactivar/<int:id>', methods=['POST'])
def reactivar_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)
    
    proveedor.Activo = True  # CAMBIADO: Estado -> Activo
    db.session.commit()
    
    flash('Proveedor reactivado exitosamente.', 'success')
    return redirect(url_for('proveedores.listar_proveedores'))