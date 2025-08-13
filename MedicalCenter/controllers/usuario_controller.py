from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models import Usuario, db
from controllers.auth_controller import login_required, admin_required

usuario_bp = Blueprint('usuario', __name__)

@usuario_bp.route('/usuarios')
@admin_required
def usuarios():
    """Página principal de usuarios"""
    if not db.connect():
        flash('Error de conexión a la base de datos', 'error')
        return render_template('usuarios.html', usuarios=[])
    
    try:
        usuarios = Usuario.get_all()
        return render_template('usuarios.html', usuarios=usuarios)
    
    except Exception as e:
        flash('Error al cargar los usuarios', 'error')
        return render_template('usuarios.html', usuarios=[])
    
    finally:
        db.disconnect()

@usuario_bp.route('/nuevo_usuario', methods=['GET', 'POST'])
@admin_required
def nuevo_usuario():
    """Crear nuevo usuario"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            rfc = request.form.get('rfc', '').strip().upper()
            nombre = request.form.get('nombre', '').strip()
            apellido_paterno = request.form.get('apellido_paterno', '').strip()
            apellido_materno = request.form.get('apellido_materno', '').strip()
            password = request.form.get('password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()
            privilegio = request.form.get('privilegio', '1')
            
            # Validar campos requeridos
            if not all([rfc, nombre, apellido_paterno, password]):
                flash('RFC, nombre, apellido paterno y contraseña son requeridos', 'error')
                return render_template('nuevo_usuario.html')
            
            # Validar confirmación de contraseña
            if password != confirm_password:
                flash('Las contraseñas no coinciden', 'error')
                return render_template('nuevo_usuario.html')
            
            # Conectar a la base de datos
            if not db.connect():
                flash('Error de conexión a la base de datos', 'error')
                return render_template('nuevo_usuario.html')
            
            # Verificar si el RFC ya existe
            if Usuario.rfc_exists(rfc):
                flash('El RFC ya está registrado en el sistema', 'error')
                return render_template('nuevo_usuario.html')
            
            # Crear el usuario
            success = Usuario.create(
                rfc=rfc,
                nombre=nombre,
                apellido_paterno=apellido_paterno,
                apellido_materno=apellido_materno,
                password=password,
                privilegio=int(privilegio)
            )
            
            if success:
                flash('Usuario creado exitosamente', 'success')
                return redirect(url_for('usuario.usuarios'))
            else:
                flash('Error al crear el usuario', 'error')
                return render_template('nuevo_usuario.html')
        
        except Exception as e:
            flash('Error al procesar el usuario', 'error')
            return render_template('nuevo_usuario.html')
        
        finally:
            db.disconnect()
    
    # GET request - mostrar formulario
    return render_template('nuevo_usuario.html')

@usuario_bp.route('/editar_usuario/<int:usuario_id>', methods=['GET', 'POST'])
@admin_required
def editar_usuario(usuario_id):
    """Editar usuario existente"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            rfc = request.form.get('rfc', '').strip().upper()
            nombre = request.form.get('nombre', '').strip()
            apellido_paterno = request.form.get('apellido_paterno', '').strip()
            apellido_materno = request.form.get('apellido_materno', '').strip()
            password = request.form.get('password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()
            privilegio = request.form.get('privilegio', '1')
            
            # Validar campos requeridos
            if not all([rfc, nombre, apellido_paterno]):
                flash('RFC, nombre y apellido paterno son requeridos', 'error')
                return redirect(url_for('usuario.editar_usuario', usuario_id=usuario_id))
            
            # Validar contraseña si se proporciona
            if password and password != confirm_password:
                flash('Las contraseñas no coinciden', 'error')
                return redirect(url_for('usuario.editar_usuario', usuario_id=usuario_id))
            
            # Conectar a la base de datos
            if not db.connect():
                flash('Error de conexión a la base de datos', 'error')
                return redirect(url_for('usuario.editar_usuario', usuario_id=usuario_id))
            
            # Verificar si el RFC ya existe (excluyendo el usuario actual)
            existing_user = Usuario.get_by_rfc(rfc)
            if existing_user and existing_user['id'] != usuario_id:
                flash('El RFC ya está registrado por otro usuario', 'error')
                return redirect(url_for('usuario.editar_usuario', usuario_id=usuario_id))
            
            # Actualizar el usuario
            success = Usuario.update(
                usuario_id=usuario_id,
                rfc=rfc,
                nombre=nombre,
                apellido_paterno=apellido_paterno,
                apellido_materno=apellido_materno,
                password=password if password else None,
                privilegio=int(privilegio)
            )
            
            if success:
                flash('Usuario actualizado exitosamente', 'success')
                return redirect(url_for('usuario.usuarios'))
            else:
                flash('Error al actualizar el usuario', 'error')
                return redirect(url_for('usuario.editar_usuario', usuario_id=usuario_id))
        
        except Exception as e:
            flash('Error al procesar la actualización', 'error')
            return redirect(url_for('usuario.editar_usuario', usuario_id=usuario_id))
        
        finally:
            db.disconnect()
    
    # GET request - mostrar formulario de edición
    if not db.connect():
        flash('Error de conexión a la base de datos', 'error')
        return redirect(url_for('usuario.usuarios'))
    
    try:
        usuario = Usuario.get_by_id(usuario_id)
        if not usuario:
            flash('Usuario no encontrado', 'error')
            return redirect(url_for('usuario.usuarios'))
        
        return render_template('editar_usuario.html', usuario=usuario)
    
    except Exception as e:
        flash('Error al cargar los datos del usuario', 'error')
        return redirect(url_for('usuario.usuarios'))
    
    finally:
        db.disconnect()

@usuario_bp.route('/eliminar_usuario/<int:usuario_id>', methods=['POST'])
@admin_required
def eliminar_usuario(usuario_id):
    """Eliminar usuario"""
    # Prevenir que el usuario se elimine a sí mismo
    if session.get('user_id') == usuario_id:
        flash('No puede eliminar su propia cuenta', 'error')
        return redirect(url_for('usuario.usuarios'))
    
    if not db.connect():
        flash('Error de conexión a la base de datos', 'error')
        return redirect(url_for('usuario.usuarios'))
    
    try:
        success = Usuario.delete(usuario_id)
        
        if success:
            flash('Usuario eliminado exitosamente', 'success')
        else:
            flash('Error al eliminar el usuario', 'error')
    
    except Exception as e:
        flash('Error al procesar la eliminación', 'error')
    
    finally:
        db.disconnect()
    
    return redirect(url_for('usuario.usuarios'))

@usuario_bp.route('/cambiar_password', methods=['GET', 'POST'])
@login_required
def cambiar_password():
    """Cambiar contraseña del usuario actual"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            current_password = request.form.get('current_password', '').strip()
            new_password = request.form.get('new_password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()
            
            # Validar campos requeridos
            if not all([current_password, new_password, confirm_password]):
                flash('Todos los campos son requeridos', 'error')
                return render_template('cambiar_password.html')
            
            # Validar confirmación de contraseña
            if new_password != confirm_password:
                flash('Las contraseñas nuevas no coinciden', 'error')
                return render_template('cambiar_password.html')
            
            # Conectar a la base de datos
            if not db.connect():
                flash('Error de conexión a la base de datos', 'error')
                return render_template('cambiar_password.html')
            
            # Verificar contraseña actual
            user_rfc = session.get('user_rfc')
            if not Usuario.authenticate(user_rfc, current_password):
                flash('La contraseña actual es incorrecta', 'error')
                return render_template('cambiar_password.html')
            
            # Actualizar contraseña
            user_id = session.get('user_id')
            success = Usuario.update(
                usuario_id=user_id,
                password=new_password
            )
            
            if success:
                flash('Contraseña actualizada exitosamente', 'success')
                return redirect(url_for('cita.citas'))
            else:
                flash('Error al actualizar la contraseña', 'error')
                return render_template('cambiar_password.html')
        
        except Exception as e:
            flash('Error al procesar el cambio de contraseña', 'error')
            return render_template('cambiar_password.html')
        
        finally:
            db.disconnect()
    
    # GET request - mostrar formulario
    return render_template('cambiar_password.html')

@usuario_bp.route('/perfil')
@login_required
def perfil():
    """Ver perfil del usuario actual"""
    if not db.connect():
        flash('Error de conexión a la base de datos', 'error')
        return redirect(url_for('cita.citas'))
    
    try:
        user_id = session.get('user_id')
        usuario = Usuario.get_by_id(user_id)
        
        if not usuario:
            flash('Usuario no encontrado', 'error')
            return redirect(url_for('cita.citas'))
        
        return render_template('perfil.html', usuario=usuario)
    
    except Exception as e:
        flash('Error al cargar el perfil', 'error')
        return redirect(url_for('cita.citas'))
    
    finally:
        db.disconnect()

@usuario_bp.route('/api/usuarios')
@admin_required
def api_usuarios():
    """API para obtener lista de usuarios"""
    if not db.connect():
        return jsonify({'error': 'Error de conexión a la base de datos'}), 500
    
    try:
        usuarios = Usuario.get_all()
        return jsonify({'usuarios': usuarios})
    
    except Exception as e:
        return jsonify({'error': 'Error al obtener los usuarios'}), 500
    
    finally:
        db.disconnect()