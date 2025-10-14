from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models.productos import Producto
from app.models.categorias import Categoria
from app.models.proveedores import Proveedor
from app import db
from decimal import Decimal

# Blueprint Productos
productos_bp = Blueprint('productos', __name__, url_prefix='/productos')

# ========================
# RF-009: Crear Producto
# ========================
@productos_bp.route('/crear', methods=['GET', 'POST'])
def crear_producto():
    categorias = Categoria.query.filter_by(Activo=True).all()
    proveedores = Proveedor.query.filter_by(Activo=True).all()
    
    if request.method == 'POST':
        nombre = request.form['nombre'].strip()
        descripcion = request.form.get('descripcion', '').strip()
        codigo_sku = request.form['codigo_sku'].strip().upper()
        cantidad_actual = int(request.form.get('cantidad_actual', 0))
        unidad_medida = request.form['unidad_medida'].strip()
        stock_minimo = int(request.form.get('stock_minimo', 0))
        precio_unitario = Decimal(request.form['precio_unitario'])
        categoria_id = int(request.form['categoria_id'])
        proveedor_id = int(request.form['proveedor_id'])
        
        # --- Validaciones ---
        errores = []
        if not nombre:
            errores.append('El nombre es obligatorio.')
        if not codigo_sku:
            errores.append('El código SKU es obligatorio.')
        if len(codigo_sku) > 50:
            errores.append('El código SKU no puede exceder 50 caracteres.')
        if not unidad_medida:
            errores.append('La unidad de medida es obligatoria.')
        if cantidad_actual < 0:
            errores.append('La cantidad actual debe ser un número positivo.')
        if stock_minimo < 0:
            errores.append('El stock mínimo debe ser mayor o igual a 0.')
        if precio_unitario <= 0:
            errores.append('El precio unitario debe ser mayor a 0.')
        
        # Validar código SKU único
        sku_existente = Producto.query.filter_by(CodigoSKU=codigo_sku).first()
        if sku_existente:
            errores.append('El código SKU ya existe en el sistema.')
        
        if errores:
            for error in errores:
                flash(error, 'danger')
            return render_template('productos/crear.html', 
                                   categorias=categorias, 
                                   proveedores=proveedores)
        
        # --- Crear Producto ---
        nuevo_producto = Producto(
            Nombre=nombre,
            Descripcion=descripcion,
            CodigoSKU=codigo_sku,
            CantidadActual=cantidad_actual,
            UnidadMedida=unidad_medida,
            StockMinimo=stock_minimo,
            PrecioUnitario=precio_unitario,
            CategoriaId=categoria_id,
            ProveedorId=proveedor_id
        )
        
        db.session.add(nuevo_producto)
        db.session.commit()
        
        flash('Producto creado exitosamente.', 'success')
        return redirect(url_for('productos.listar_productos'))
    
    return render_template('productos/crear.html', 
                           categorias=categorias, 
                           proveedores=proveedores)

# ========================
# RF-010: Listar Productos
# ========================
@productos_bp.route('/')
def listar_productos():
    search = request.args.get('search', '')
    categoria_id = request.args.get('categoria_id', '')
    estado = request.args.get('estado', '')
    sort_by = request.args.get('sort_by', 'nombre')
    
    query = Producto.query.join(Categoria).join(Proveedor)
    
    # --- Filtros ---
    if search:
        query = query.filter(
            (Producto.Nombre.ilike(f'%{search}%')) | 
            (Producto.CodigoSKU.ilike(f'%{search}%'))
        )
    
    if categoria_id:
        query = query.filter(Producto.CategoriaId == categoria_id)
    
    # Filtro por estado de stock
    if estado:
        if estado == 'normal':
            query = query.filter(Producto.CantidadActual > Producto.StockMinimo)
        elif estado == 'bajo':
            query = query.filter(
                (Producto.CantidadActual <= Producto.StockMinimo) & 
                (Producto.CantidadActual > 0)
            )
        elif estado == 'critico':
            query = query.filter(Producto.CantidadActual == 0)
    
    # --- Orden ---
    if sort_by == 'cantidad':
        query = query.order_by(Producto.CantidadActual.desc())
    elif sort_by == 'precio':
        query = query.order_by(Producto.PrecioUnitario.desc())
    else:
        query = query.order_by(Producto.Nombre.asc())
    
    productos = query.all()
    categorias = Categoria.query.filter_by(Activo=True).all()
    
    return render_template('productos/lista.html', 
                           productos=productos, 
                           categorias=categorias)

# ========================
# API: Productos (opcional)
# ========================
@productos_bp.route('/api/productos')
def api_productos():
    productos = Producto.query.filter_by(Activo=True).all()
    return jsonify([
        {
            'id': p.Id,
            'nombre': p.Nombre,
            'codigo_sku': p.CodigoSKU,
            'cantidad': p.CantidadActual,
            'stock_minimo': p.StockMinimo,
            'estado': p.estado_stock() if hasattr(p, 'estado_stock') else 'N/A'
        }
        for p in productos
    ])