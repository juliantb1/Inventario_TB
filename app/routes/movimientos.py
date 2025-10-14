from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models.movimientos import Movimiento
from app.models.productos import Producto
from app import db
from decimal import Decimal
from datetime import datetime

# Blueprint Movimientos
movimientos_bp = Blueprint('movimientos', __name__, url_prefix='/movimientos')

# ========================
# Listar Movimientos
# ========================
@movimientos_bp.route('/')
def listar_movimientos():
    # Obtener parámetros de filtro
    producto_id = request.args.get('producto_id', '')
    tipo = request.args.get('tipo', '')
    
    # Consulta base
    query = Movimiento.query.join(Producto, Producto.Id == Movimiento.ProductoId)
    
    # Aplicar filtros
    if producto_id:
        query = query.filter(Movimiento.ProductoId == producto_id)
    
    if tipo:
        query = query.filter(Movimiento.Tipo == tipo)
    
    # Ordenar por fecha más reciente primero
    movimientos = query.order_by(Movimiento.FechaCreacion.desc()).all()
    productos = Producto.query.filter_by(Activo=True).all()
    
    return render_template('movimientos/lista.html', 
                           movimientos=movimientos, 
                           productos=productos)

# ========================
# Registrar Entrada de Stock
# ========================
@movimientos_bp.route('/entrada', methods=['GET', 'POST'])
def registrar_entrada():
    productos = Producto.query.filter_by(Activo=True).all()
    
    if request.method == 'POST':
        try:
            producto_id = int(request.form['producto_id'])
            cantidad = Decimal(request.form['cantidad'])
            motivo = request.form.get('motivo', '').strip()
            notas = request.form.get('notas', '').strip()
            
            producto = Producto.query.get_or_404(producto_id)
            
            # Validaciones
            if cantidad <= 0:
                flash('La cantidad debe ser mayor a 0.', 'danger')
                return render_template('movimientos/entrada.html', productos=productos)
            
            # Crear movimiento de entrada
            nuevo_movimiento = Movimiento(
                ProductoId=producto_id,
                Tipo='entrada',
                Cantidad=cantidad,
                Motivo=motivo,
                Notas=notas,
                Usuario="Sistema",
                FechaCreacion=datetime.utcnow()
            )
            
            # Actualizar stock del producto
            producto.CantidadActual += float(cantidad)
            
            db.session.add(nuevo_movimiento)
            db.session.commit()
            
            flash(f'Entrada de {cantidad} unidades registrada exitosamente.', 'success')
            return redirect(url_for('movimientos.listar_movimientos'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar entrada: {str(e)}', 'danger')
            return render_template('movimientos/entrada.html', productos=productos)
    
    return render_template('movimientos/entrada.html', productos=productos)

# ========================
# Registrar Salida de Stock
# ========================
@movimientos_bp.route('/salida', methods=['GET', 'POST'])
def registrar_salida():
    productos = Producto.query.filter_by(Activo=True).all()
    
    if request.method == 'POST':
        try:
            producto_id = int(request.form['producto_id'])
            cantidad = Decimal(request.form['cantidad'])
            motivo = request.form.get('motivo', '').strip()
            notas = request.form.get('notas', '').strip()
            
            producto = Producto.query.get_or_404(producto_id)
            
            # Validaciones
            if cantidad <= 0:
                flash('La cantidad debe ser mayor a 0.', 'danger')
                return render_template('movimientos/salida.html', productos=productos)
            
            if cantidad > Decimal(str(producto.CantidadActual)):
                flash(f'No hay suficiente stock. Stock actual: {producto.CantidadActual}', 'danger')
                return render_template('movimientos/salida.html', productos=productos)
            
            # Crear movimiento de salida
            nuevo_movimiento = Movimiento(
                ProductoId=producto_id,
                Tipo='salida',
                Cantidad=cantidad,
                Motivo=motivo,
                Notas=notas,
                Usuario="Sistema",
                FechaCreacion=datetime.utcnow()
            )
            
            # Actualizar stock del producto
            producto.CantidadActual -= float(cantidad)
            
            db.session.add(nuevo_movimiento)
            db.session.commit()
            
            flash(f'Salida de {cantidad} unidades registrada exitosamente.', 'success')
            return redirect(url_for('movimientos.listar_movimientos'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar salida: {str(e)}', 'danger')
            return render_template('movimientos/salida.html', productos=productos)
    
    return render_template('movimientos/salida.html', productos=productos)

# ========================
# API: Movimientos por Producto
# ========================
@movimientos_bp.route('/api/producto/<int:producto_id>')
def movimientos_por_producto(producto_id):
    try:
        movimientos = Movimiento.query.filter_by(ProductoId=producto_id)\
            .order_by(Movimiento.FechaCreacion.desc())\
            .limit(10)\
            .all()
        
        return jsonify([
            {
                'id': m.Id,
                'tipo': m.Tipo,
                'cantidad': float(m.Cantidad),
                'fecha': m.FechaCreacion.strftime('%Y-%m-%d %H:%M') if m.FechaCreacion else 'N/A',
                'motivo': m.Motivo,
                'usuario': m.Usuario
            }
            for m in movimientos
        ])
    except Exception as e:
        return jsonify({'error': str(e)}), 500