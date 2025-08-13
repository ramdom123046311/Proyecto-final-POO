from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models import Paciente, db
from models.cita import Cita
from controllers.auth_controller import login_required

paciente_bp = Blueprint('paciente', __name__)

@paciente_bp.route('/pacientes', methods=['GET', 'POST'])
@login_required
def pacientes():
    """Página principal de pacientes"""
    if request.method == 'POST':
        # Verificar si es una acción de eliminación
        action = request.form.get('action')
        if action == 'delete':
            # Manejar eliminación de paciente
            paciente_id = request.form.get('id_paciente')
            if paciente_id:
                if not db.connect():
                    flash('Error de conexión a la base de datos', 'error')
                else:
                    try:
                        # Verificar si el paciente tiene citas asociadas
                        citas_paciente = Cita.get_by_patient(int(paciente_id))
                        
                        if citas_paciente:
                            flash('No se puede eliminar el paciente porque tiene citas asociadas. Primero debe cancelar o reasignar las citas.', 'error')
                        else:
                            success = Paciente.delete(int(paciente_id))
                            if success:
                                flash('Paciente eliminado exitosamente', 'success')
                            else:
                                flash('Error al eliminar el paciente', 'error')
                    except Exception as e:
                        flash('Error al procesar la eliminación', 'error')
                    finally:
                        db.disconnect()
            return redirect(url_for('paciente.pacientes'))
        
        elif action == 'update':
            # Manejar actualización de paciente
            paciente_id = request.form.get('id_paciente')
            if paciente_id:
                try:
                    # Obtener datos del formulario
                    nombres = request.form.get('nombres', '').strip()
                    apellidos = request.form.get('apellidos', '').strip()
                    fecha_nacimiento = request.form.get('fecha_nacimiento')
                    genero = request.form.get('genero')
                    tipo_sangre = request.form.get('tipo_sangre', '').strip()
                    alergias = request.form.get('alergias', '').strip()
                    
                    # Validaciones básicas
                    if not all([nombres, apellidos, fecha_nacimiento, genero, tipo_sangre]):
                        flash('Todos los campos obligatorios deben ser completados', 'error')
                        return redirect(url_for('paciente.pacientes'))
                    
                    # Conectar a la base de datos
                    if not db.connect():
                        flash('Error de conexión a la base de datos', 'error')
                        return redirect(url_for('paciente.pacientes'))
                    
                    # Actualizar el paciente
                    success = Paciente.update(
                        paciente_id=int(paciente_id),
                        nombres=nombres,
                        apellidos=apellidos,
                        fecha_nacimiento=fecha_nacimiento,
                        genero=genero,
                        tipo_sangre=tipo_sangre,
                        alergias=alergias if alergias else None
                    )
                    
                    if success:
                        flash('Paciente actualizado exitosamente', 'success')
                    else:
                        flash('Error al actualizar el paciente', 'error')
                        
                except Exception as e:
                    flash('Error al procesar la actualización', 'error')
                finally:
                    db.disconnect()
            return redirect(url_for('paciente.pacientes'))
        
        # Manejar creación de paciente
        try:
            # Obtener datos del formulario
            nombres = request.form.get('nombres', '').strip()
            apellidos = request.form.get('apellidos', '').strip()
            fecha_nacimiento = request.form.get('fecha_nacimiento')
            genero = request.form.get('genero')
            tipo_sangre = request.form.get('tipo_sangre', '').strip()
            alergias = request.form.get('alergias', '').strip()
            
            # Validaciones del servidor
            errores = {}
            
            if not nombres:
                errores['nombres'] = 'Los nombres son requeridos'
            elif len(nombres) < 2:
                errores['nombres'] = 'Los nombres deben tener al menos 2 caracteres'
            elif not nombres.replace(' ', '').isalpha():
                errores['nombres'] = 'Los nombres solo pueden contener letras'
            
            if not apellidos:
                errores['apellidos'] = 'Los apellidos son requeridos'
            elif len(apellidos) < 2:
                errores['apellidos'] = 'Los apellidos deben tener al menos 2 caracteres'
            elif not apellidos.replace(' ', '').isalpha():
                errores['apellidos'] = 'Los apellidos solo pueden contener letras'
            
            if not fecha_nacimiento:
                errores['fecha_nacimiento'] = 'La fecha de nacimiento es requerida'
            else:
                from datetime import datetime
                try:
                    fecha_nac = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
                    if fecha_nac.date() > datetime.now().date():
                        errores['fecha_nacimiento'] = 'La fecha de nacimiento no puede ser en el futuro'
                except ValueError:
                    errores['fecha_nacimiento'] = 'Formato de fecha inválido'
            
            if not genero:
                errores['genero'] = 'El género es requerido'
            elif genero not in ['Masculino', 'Femenino']:
                errores['genero'] = 'El género debe ser Masculino o Femenino'
            
            if not tipo_sangre:
                errores['tipo_sangre'] = 'El tipo de sangre es requerido'
            elif tipo_sangre not in ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-', 'Desconocido']:
                errores['tipo_sangre'] = 'Tipo de sangre inválido'
            
            if errores:
                for campo, mensaje in errores.items():
                    flash(mensaje, 'error')
            else:
                # Conectar a la base de datos
                if not db.connect():
                    flash('Error de conexión a la base de datos', 'error')
                else:
                    # Crear el paciente
                    success = Paciente.create(
                        nombres=nombres,
                        apellidos=apellidos,
                        fecha_nacimiento=fecha_nacimiento,
                        genero=genero,
                        tipo_sangre=tipo_sangre,
                        alergias=alergias if alergias else None
                    )
                    
                    if success:
                        flash('Paciente creado exitosamente', 'success')
                    else:
                        flash('Error al crear el paciente', 'error')
                        
        except Exception as e:
            flash('Error al procesar la solicitud', 'error')
        finally:
            db.disconnect()
            
        return redirect(url_for('paciente.pacientes'))
    
    # GET request - mostrar lista de pacientes
    if not db.connect():
        flash('Error de conexión a la base de datos', 'error')
        return render_template('pacientes.html', pacientes=[])
    
    try:
        # Obtener término de búsqueda si existe
        search_term = request.args.get('search', '').strip()
        
        if search_term:
            pacientes = Paciente.search(search_term)
        else:
            pacientes = Paciente.get_all()
        

        return render_template('pacientes.html', pacientes=pacientes, search_term=search_term)
    
    except Exception as e:
        flash('Error al cargar los pacientes', 'error')
        return render_template('pacientes.html', pacientes=[])
    
    finally:
        db.disconnect()

@paciente_bp.route('/nuevo_paciente', methods=['GET', 'POST'])
@login_required
def nuevo_paciente():
    """Crear nuevo paciente"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre = request.form.get('nombre', '').strip()
            apellido_paterno = request.form.get('apellido_paterno', '').strip()
            apellido_materno = request.form.get('apellido_materno', '').strip()
            fecha_nacimiento = request.form.get('fecha_nacimiento')
            genero = request.form.get('genero')
            telefono = request.form.get('telefono', '').strip()
            email = request.form.get('email', '').strip()
            direccion = request.form.get('direccion', '').strip()
            contacto_emergencia = request.form.get('contacto_emergencia', '').strip()
            telefono_emergencia = request.form.get('telefono_emergencia', '').strip()
            alergias = request.form.get('alergias', '').strip()
            medicamentos_actuales = request.form.get('medicamentos_actuales', '').strip()
            historial_medico = request.form.get('historial_medico', '').strip()
            
            # Validar campos requeridos
            if not all([nombre, apellido_paterno, fecha_nacimiento, genero]):
                flash('Nombre, apellido paterno, fecha de nacimiento y género son requeridos', 'error')
                return render_template('nuevo_paciente.html')
            
            # Conectar a la base de datos
            if not db.connect():
                flash('Error de conexión a la base de datos', 'error')
                return render_template('nuevo_paciente.html')
            
            # Combinar nombres y apellidos según la estructura de la tabla
            nombres_completos = nombre
            apellidos_completos = apellido_paterno
            if apellido_materno:
                apellidos_completos += f" {apellido_materno}"
            
            # Crear el paciente (solo campos que existen en la tabla)
            success = Paciente.create(
                nombres=nombres_completos,
                apellidos=apellidos_completos,
                fecha_nacimiento=fecha_nacimiento,
                genero=genero,
                tipo_sangre="O+",  # Valor por defecto, ya que es requerido
                alergias=alergias
            )
            
            if success:
                flash('Paciente creado exitosamente', 'success')
                return redirect(url_for('paciente.pacientes'))
            else:
                flash('Error al crear el paciente', 'error')
                return render_template('nuevo_paciente.html')
        
        except Exception as e:
            flash('Error al procesar el paciente', 'error')
            return render_template('nuevo_paciente.html')
        
        finally:
            db.disconnect()
    
    # GET request - mostrar formulario
    return render_template('nuevo_paciente.html')

@paciente_bp.route('/editar_paciente/<int:paciente_id>', methods=['GET', 'POST'])
@login_required
def editar_paciente(paciente_id):
    """Editar paciente existente"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre = request.form.get('nombre', '').strip()
            apellido_paterno = request.form.get('apellido_paterno', '').strip()
            apellido_materno = request.form.get('apellido_materno', '').strip()
            fecha_nacimiento = request.form.get('fecha_nacimiento')
            genero = request.form.get('genero')
            telefono = request.form.get('telefono', '').strip()
            email = request.form.get('email', '').strip()
            direccion = request.form.get('direccion', '').strip()
            contacto_emergencia = request.form.get('contacto_emergencia', '').strip()
            telefono_emergencia = request.form.get('telefono_emergencia', '').strip()
            alergias = request.form.get('alergias', '').strip()
            medicamentos_actuales = request.form.get('medicamentos_actuales', '').strip()
            historial_medico = request.form.get('historial_medico', '').strip()
            
            # Validaciones del servidor
            errores = {}
            
            if not nombre:
                errores['nombre'] = 'El nombre es requerido'
            elif len(nombre) < 2:
                errores['nombre'] = 'El nombre debe tener al menos 2 caracteres'
            elif not nombre.replace(' ', '').isalpha():
                errores['nombre'] = 'El nombre solo puede contener letras'
            
            if not apellido_paterno:
                errores['apellido_paterno'] = 'El apellido paterno es requerido'
            elif len(apellido_paterno) < 2:
                errores['apellido_paterno'] = 'El apellido paterno debe tener al menos 2 caracteres'
            elif not apellido_paterno.replace(' ', '').isalpha():
                errores['apellido_paterno'] = 'El apellido paterno solo puede contener letras'
            
            if apellido_materno and not apellido_materno.replace(' ', '').isalpha():
                errores['apellido_materno'] = 'El apellido materno solo puede contener letras'
            
            if not fecha_nacimiento:
                errores['fecha_nacimiento'] = 'La fecha de nacimiento es requerida'
            else:
                from datetime import datetime
                try:
                    fecha_nac = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
                    if fecha_nac.date() > datetime.now().date():
                        errores['fecha_nacimiento'] = 'La fecha de nacimiento no puede ser en el futuro'
                except ValueError:
                    errores['fecha_nacimiento'] = 'Formato de fecha inválido'
            
            if not genero:
                errores['genero'] = 'El género es requerido'
            elif genero not in ['Masculino', 'Femenino']:
                errores['genero'] = 'El género debe ser Masculino o Femenino'
            
            if telefono and (len(telefono) < 10 or not telefono.replace('-', '').replace(' ', '').isdigit()):
                errores['telefono'] = 'El teléfono debe tener al menos 10 dígitos'
            
            import re
            if email and not re.match(r'^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$', email):
                errores['email'] = 'El formato del email no es válido'
            
            if errores:
                for campo, mensaje in errores.items():
                    flash(mensaje, 'error')
                return redirect(url_for('paciente.editar_paciente', paciente_id=paciente_id))
            
            # Conectar a la base de datos
            if not db.connect():
                flash('Error de conexión a la base de datos', 'error')
                return redirect(url_for('paciente.editar_paciente', paciente_id=paciente_id))
            
            # Combinar nombres y apellidos según la estructura de la tabla
            nombres_completos = nombre
            apellidos_completos = apellido_paterno
            if apellido_materno:
                apellidos_completos += f" {apellido_materno}"
            
            # Actualizar el paciente (solo campos que existen en la tabla)
            success = Paciente.update(
                paciente_id=paciente_id,
                nombres=nombres_completos,
                apellidos=apellidos_completos,
                fecha_nacimiento=fecha_nacimiento,
                genero=genero,
                tipo_sangre="O+",  # Valor por defecto, ya que es requerido
                alergias=alergias
            )
            
            if success:
                flash('Paciente actualizado exitosamente', 'success')
                return redirect(url_for('paciente.pacientes'))
            else:
                flash('Error al actualizar el paciente', 'error')
                return redirect(url_for('paciente.editar_paciente', paciente_id=paciente_id))
        
        except Exception as e:
            flash('Error al procesar la actualización', 'error')
            return redirect(url_for('paciente.editar_paciente', paciente_id=paciente_id))
        
        finally:
            db.disconnect()
    
    # GET request - mostrar formulario de edición
    if not db.connect():
        flash('Error de conexión a la base de datos', 'error')
        return redirect(url_for('paciente.pacientes'))
    
    try:
        paciente = Paciente.get_by_id(paciente_id)
        if not paciente:
            flash('Paciente no encontrado', 'error')
            return redirect(url_for('paciente.pacientes'))
        
        return render_template('editar_paciente.html', paciente=paciente)
    
    except Exception as e:
        flash('Error al cargar los datos del paciente', 'error')
        return redirect(url_for('paciente.pacientes'))
    
    finally:
        db.disconnect()

@paciente_bp.route('/eliminar_paciente/<int:paciente_id>', methods=['POST'])
@login_required
def eliminar_paciente(paciente_id):
    """Eliminar paciente"""
    if not db.connect():
        flash('Error de conexión a la base de datos', 'error')
        return redirect(url_for('paciente.pacientes'))
    
    try:
        # Verificar si el paciente tiene citas asociadas
        citas_paciente = Cita.get_by_patient(paciente_id)
        
        if citas_paciente:
            flash('No se puede eliminar el paciente porque tiene citas asociadas. Primero debe cancelar o reasignar las citas.', 'error')
            return redirect(url_for('paciente.pacientes'))
        
        success = Paciente.delete(paciente_id)
        
        if success:
            flash('Paciente eliminado exitosamente', 'success')
        else:
            flash('Error al eliminar el paciente', 'error')
    
    except Exception as e:
        flash('Error al procesar la eliminación', 'error')
    
    finally:
        db.disconnect()
    
    return redirect(url_for('paciente.pacientes'))

@paciente_bp.route('/ver_paciente/<int:paciente_id>')
@login_required
def ver_paciente(paciente_id):
    """Ver detalles del paciente"""
    if not db.connect():
        flash('Error de conexión a la base de datos', 'error')
        return redirect(url_for('paciente.pacientes'))
    
    try:
        paciente = Paciente.get_by_id(paciente_id)
        if not paciente:
            flash('Paciente no encontrado', 'error')
            return redirect(url_for('paciente.pacientes'))
        
        return render_template('ver_paciente.html', paciente=paciente)
    
    except Exception as e:
        flash('Error al cargar los datos del paciente', 'error')
        return redirect(url_for('paciente.pacientes'))
    
    finally:
        db.disconnect()

@paciente_bp.route('/api/pacientes')
@login_required
def api_pacientes():
    """API para obtener lista de pacientes"""
    if not db.connect():
        return jsonify({'error': 'Error de conexión a la base de datos'}), 500
    
    try:
        pacientes = Paciente.get_all()
        return jsonify({'pacientes': pacientes})
    
    except Exception as e:
        return jsonify({'error': 'Error al obtener los pacientes'}), 500
    
    finally:
        db.disconnect()

@paciente_bp.route('/api/buscar_pacientes')
@login_required
def api_buscar_pacientes():
    """API para buscar pacientes"""
    search_term = request.args.get('q', '').strip()
    
    if not search_term:
        return jsonify({'pacientes': []})
    
    if not db.connect():
        return jsonify({'error': 'Error de conexión a la base de datos'}), 500
    
    try:
        pacientes = Paciente.search(search_term)
        return jsonify({'pacientes': pacientes})
    
    except Exception as e:
        return jsonify({'error': 'Error al buscar pacientes'}), 500
    
    finally:
        db.disconnect()