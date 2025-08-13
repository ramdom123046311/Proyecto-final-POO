from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import Usuario, db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        rfc = request.form.get('rfc', '').strip()
        password = request.form.get('password', '').strip()
        
        # Validaciones del servidor
        errores = {}
        
        if not rfc:
            errores['rfc'] = 'El RFC es requerido'
        elif len(rfc) < 10 or len(rfc) > 13:
            errores['rfc'] = 'El RFC debe tener entre 10 y 13 caracteres'
        
        if not password:
            errores['password'] = 'La contraseña es requerida'
        elif len(password) < 5:
            errores['password'] = 'La contraseña debe tener al menos 5 caracteres'
        
        if errores:
            for campo, mensaje in errores.items():
                flash(mensaje, 'error')
            return render_template('index.html')
        
        # Conectar a la base de datos
        if not db.connect():
            flash('Error de conexión a la base de datos', 'error')
            return render_template('index.html')
        
        try:
            # Autenticar usuario
            user = Usuario.authenticate(rfc, password)
            
            if user:
                # Crear sesión
                session['user_id'] = user['id']
                session['user_rfc'] = user['rfc']
                session['user_name'] = f"{user['nombre']} {user['apellido_paterno']}"
                session['user_privilege'] = user['privilegio']
                
                flash(f'Bienvenido, {session["user_name"]}', 'success')
                return redirect(url_for('cita.citas'))
            else:
                flash('RFC o contraseña incorrectos', 'error')
                return render_template('index.html')
        
        except Exception as e:
            flash('Error durante la autenticación', 'error')
            return render_template('index.html')
        
        finally:
            db.disconnect()
    
    # Si ya está logueado, redirigir a citas
    if 'user_id' in session:
        return redirect(url_for('cita.citas'))
    
    return render_template('index.html')

@auth_bp.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('auth.login'))

# Función auxiliar para verificar autenticación
def login_required(f):
    """Decorador para rutas que requieren autenticación"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debe iniciar sesión para acceder a esta página', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# Función auxiliar para verificar privilegios
def admin_required(f):
    """Decorador para rutas que requieren privilegios de administrador"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debe iniciar sesión para acceder a esta página', 'warning')
            return redirect(url_for('auth.login'))
        
        if session.get('user_privilege', 0) < 2:
            flash('No tiene permisos para acceder a esta página', 'error')
            return redirect(url_for('cita.citas'))
        
        return f(*args, **kwargs)
    return decorated_function