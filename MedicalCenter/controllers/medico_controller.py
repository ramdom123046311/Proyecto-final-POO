from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models import Medico, db
from models.cita import Cita
from controllers.auth_controller import login_required, admin_required

medico_bp = Blueprint('medico', __name__)

@medico_bp.route('/medicos', methods=['GET', 'POST'])
@login_required
def medicos():
    """Página principal de médicos"""
    if request.method == 'POST':
        # Verificar si es una acción de eliminación
        action = request.form.get('action')
        if action == 'delete':
            # Manejar eliminación de médico
            medico_id = request.form.get('id_medico')
            if medico_id:
                if not db.connect():
                    flash('Error de conexión a la base de datos', 'error')
                else:
                    try:
                        # Verificar si el médico tiene citas asociadas
                        citas_medico = Cita.get_by_doctor(int(medico_id))
                        
                        if citas_medico:
                            flash('No se puede eliminar el médico porque tiene citas asociadas. Primero debe cancelar o reasignar las citas.', 'error')
                        else:
                            success = Medico.delete(int(medico_id))
                            if success:
                                flash('Médico eliminado exitosamente', 'success')
                            else:
                                flash('Error al eliminar el médico', 'error')
                    except Exception as e:
                        flash('Error al procesar la eliminación', 'error')
                    finally:
                        db.disconnect()
            return redirect(url_for('medico.medicos'))
        
        # Manejar creación de médico
        try:
            # Obtener datos del formulario
            primer_nombre = request.form.get('primer_nombre', '').strip()
            segundo_nombre = request.form.get('segundo_nombre', '').strip()
            apellido_paterno = request.form.get('apellido_paterno', '').strip()
            apellido_materno = request.form.get('apellido_materno', '').strip()
            especialidad = request.form.get('especialidad', '').strip()
            cedula_profesional = request.form.get('cedula_profesional', '').strip()
            telefono = request.form.get('telefono', '').strip()
            correo = request.form.get('correo', '').strip()
            rfc = request.form.get('rfc', '').strip()
            centro_medico = request.form.get('centro_medico', '').strip()
            contrasena = request.form.get('contrasena', '').strip()
            
            # Validar campos requeridos
            if not all([primer_nombre, apellido_paterno, especialidad, cedula_profesional, correo, rfc, telefono, centro_medico, contrasena]):
                flash('Todos los campos marcados son requeridos', 'error')
            else:
                # Conectar a la base de datos
                if not db.connect():
                    flash('Error de conexión a la base de datos', 'error')
                else:
                    # Crear el médico
                    success = Medico.create(
                        primer_nombre=primer_nombre,
                        segundo_nombre=segundo_nombre,
                        apellido_paterno=apellido_paterno,
                        apellido_materno=apellido_materno,
                        especialidad=especialidad,
                        cedula_profesional=cedula_profesional,
                        telefono=telefono,
                        correo=correo,
                        rfc=rfc,
                        centro_medico=centro_medico,
                        contrasena=contrasena
                    )
                    
                    if success:
                        flash('Médico creado exitosamente', 'success')
                    else:
                        flash('Error al crear el médico', 'error')
                    
                    db.disconnect()
        
        except Exception as e:
            flash(f'Error al procesar la solicitud: {str(e)}', 'error')
        
        return redirect(url_for('medico.medicos'))
    
    # Manejar GET request
    if not db.connect():
        flash('Error de conexión a la base de datos', 'error')
        return render_template('medicos.html', medicos=[])
    
    try:
        # Obtener término de búsqueda si existe
        search_term = request.args.get('search', '').strip()
        
        if search_term:
            medicos = Medico.search(search_term)
        else:
            medicos = Medico.get_all()
        
        return render_template('medicos.html', medicos=medicos, search_term=search_term)
    
    except Exception as e:
        flash('Error al cargar los médicos', 'error')
        return render_template('medicos.html', medicos=[])
    
    finally:
        db.disconnect()

@medico_bp.route('/nuevo_medico', methods=['GET', 'POST'])
@admin_required
def nuevo_medico():
    """Crear nuevo médico"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre = request.form.get('nombre', '').strip()
            apellido_paterno = request.form.get('apellido_paterno', '').strip()
            apellido_materno = request.form.get('apellido_materno', '').strip()
            especialidad = request.form.get('especialidad', '').strip()
            cedula_profesional = request.form.get('cedula_profesional', '').strip()
            telefono = request.form.get('telefono', '').strip()
            email = request.form.get('email', '').strip()
            horario_inicio = request.form.get('horario_inicio')
            horario_fin = request.form.get('horario_fin')
            
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
            
            if not especialidad:
                errores['especialidad'] = 'La especialidad es requerida'
            
            if not cedula_profesional:
                errores['cedula_profesional'] = 'La cédula profesional es requerida'
            elif len(cedula_profesional) < 6:
                errores['cedula_profesional'] = 'La cédula profesional debe tener al menos 6 caracteres'
            elif not cedula_profesional.isdigit():
                errores['cedula_profesional'] = 'La cédula profesional solo puede contener números'
            
            if telefono and (len(telefono) < 10 or not telefono.replace('-', '').replace(' ', '').isdigit()):
                errores['telefono'] = 'El teléfono debe tener al menos 10 dígitos'
            
            import re
            if email and not re.match(r'^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$', email):
                errores['email'] = 'El formato del email no es válido'
            
            if errores:
                for campo, mensaje in errores.items():
                    flash(mensaje, 'error')
                return render_template('nuevo_medico.html')
            
            # Conectar a la base de datos
            if not db.connect():
                flash('Error de conexión a la base de datos', 'error')
                return render_template('nuevo_medico.html')
            
            # Crear el médico
            success = Medico.create(
                nombre=nombre,
                apellido_paterno=apellido_paterno,
                apellido_materno=apellido_materno,
                especialidad=especialidad,
                cedula_profesional=cedula_profesional,
                telefono=telefono,
                email=email,
                horario_inicio=horario_inicio,
                horario_fin=horario_fin
            )
            
            if success:
                flash('Médico creado exitosamente', 'success')
                return redirect(url_for('medico.medicos'))
            else:
                flash('Error al crear el médico', 'error')
                return render_template('nuevo_medico.html')
        
        except Exception as e:
            flash('Error al procesar el médico', 'error')
            return render_template('nuevo_medico.html')
        
        finally:
            db.disconnect()
    
    # GET request - mostrar formulario
    return render_template('nuevo_medico.html')

@medico_bp.route('/editar_medico/<int:medico_id>', methods=['GET', 'POST'])
@admin_required
def editar_medico(medico_id):
    """Editar médico existente"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre = request.form.get('nombre', '').strip()
            apellido_paterno = request.form.get('apellido_paterno', '').strip()
            apellido_materno = request.form.get('apellido_materno', '').strip()
            especialidad = request.form.get('especialidad', '').strip()
            cedula_profesional = request.form.get('cedula_profesional', '').strip()
            telefono = request.form.get('telefono', '').strip()
            email = request.form.get('email', '').strip()
            horario_inicio = request.form.get('horario_inicio')
            horario_fin = request.form.get('horario_fin')
            
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
            
            if not especialidad:
                errores['especialidad'] = 'La especialidad es requerida'
            
            if not cedula_profesional:
                errores['cedula_profesional'] = 'La cédula profesional es requerida'
            elif len(cedula_profesional) < 6:
                errores['cedula_profesional'] = 'La cédula profesional debe tener al menos 6 caracteres'
            elif not cedula_profesional.isdigit():
                errores['cedula_profesional'] = 'La cédula profesional solo puede contener números'
            
            if telefono and (len(telefono) < 10 or not telefono.replace('-', '').replace(' ', '').isdigit()):
                errores['telefono'] = 'El teléfono debe tener al menos 10 dígitos'
            
            import re
            if email and not re.match(r'^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$', email):
                errores['email'] = 'El formato del email no es válido'
            
            if errores:
                for campo, mensaje in errores.items():
                    flash(mensaje, 'error')
                return redirect(url_for('medico.editar_medico', medico_id=medico_id))
            
            # Conectar a la base de datos
            if not db.connect():
                flash('Error de conexión a la base de datos', 'error')
                return redirect(url_for('medico.editar_medico', medico_id=medico_id))
            
            # Actualizar el médico
            success = Medico.update(
                medico_id=medico_id,
                nombre=nombre,
                apellido_paterno=apellido_paterno,
                apellido_materno=apellido_materno,
                especialidad=especialidad,
                cedula_profesional=cedula_profesional,
                telefono=telefono,
                email=email,
                horario_inicio=horario_inicio,
                horario_fin=horario_fin
            )
            
            if success:
                flash('Médico actualizado exitosamente', 'success')
                return redirect(url_for('medico.medicos'))
            else:
                flash('Error al actualizar el médico', 'error')
                return redirect(url_for('medico.editar_medico', medico_id=medico_id))
        
        except Exception as e:
            flash('Error al procesar la actualización', 'error')
            return redirect(url_for('medico.editar_medico', medico_id=medico_id))
        
        finally:
            db.disconnect()
    
    # GET request - mostrar formulario de edición
    if not db.connect():
        flash('Error de conexión a la base de datos', 'error')
        return redirect(url_for('medico.medicos'))
    
    try:
        medico = Medico.get_by_id(medico_id)
        if not medico:
            flash('Médico no encontrado', 'error')
            return redirect(url_for('medico.medicos'))
        
        return render_template('editar_medico.html', medico=medico)
    
    except Exception as e:
        print(f"ERROR en ver_medico: {str(e)}")
        import traceback
        traceback.print_exc()
        flash('Error al cargar los datos del médico', 'error')
        return redirect(url_for('medico.medicos'))
    
    finally:
        db.disconnect()

@medico_bp.route('/eliminar_medico/<int:medico_id>', methods=['POST'])
@admin_required
def eliminar_medico(medico_id):
    """Eliminar médico"""
    if not db.connect():
        flash('Error de conexión a la base de datos', 'error')
        return redirect(url_for('medico.medicos'))
    
    try:
        # Verificar si el médico tiene citas asociadas
        citas_medico = Cita.get_by_doctor(medico_id)
        
        if citas_medico:
            flash('No se puede eliminar el médico porque tiene citas asociadas. Primero debe cancelar o reasignar las citas.', 'error')
            return redirect(url_for('medico.medicos'))
        
        success = Medico.delete(medico_id)
        
        if success:
            flash('Médico eliminado exitosamente', 'success')
        else:
            flash('Error al eliminar el médico', 'error')
    
    except Exception as e:
        flash('Error al procesar la eliminación', 'error')
    
    finally:
        db.disconnect()
    
    return redirect(url_for('medico.medicos'))

@medico_bp.route('/ver_medico/<int:medico_id>')
@login_required
def ver_medico(medico_id):
    """Ver detalles del médico"""
    if not db.connect():
        flash('Error de conexión a la base de datos', 'error')
        return redirect(url_for('medico.medicos'))
    
    try:
        medico = Medico.get_by_id(medico_id)
        if not medico:
            flash('Médico no encontrado', 'error')
            return redirect(url_for('medico.medicos'))
        
        return render_template('ver_medico.html', medico=medico)
    
    except Exception as e:
        print(f"ERROR en editar_medico: {str(e)}")
        import traceback
        traceback.print_exc()
        flash('Error al cargar los datos del médico', 'error')
        return redirect(url_for('medico.medicos'))
    
    finally:
        db.disconnect()

@medico_bp.route('/api/medicos')
@login_required
def api_medicos():
    """API para obtener lista de médicos"""
    if not db.connect():
        return jsonify({'error': 'Error de conexión a la base de datos'}), 500
    
    try:
        medicos = Medico.get_all()
        return jsonify({'medicos': medicos})
    
    except Exception as e:
        return jsonify({'error': 'Error al obtener los médicos'}), 500
    
    finally:
        db.disconnect()

@medico_bp.route('/api/medicos_disponibles')
@login_required
def api_medicos_disponibles():
    """API para obtener médicos disponibles para citas"""
    if not db.connect():
        return jsonify({'error': 'Error de conexión a la base de datos'}), 500
    
    try:
        medicos = Medico.get_available_for_appointments()
        return jsonify({'medicos': medicos})
    
    except Exception as e:
        return jsonify({'error': 'Error al obtener los médicos disponibles'}), 500
    
    finally:
        db.disconnect()

@medico_bp.route('/api/buscar_medicos')
@login_required
def api_buscar_medicos():
    """API para buscar médicos"""
    search_term = request.args.get('q', '').strip()
    
    if not search_term:
        return jsonify({'medicos': []})
    
    if not db.connect():
        return jsonify({'error': 'Error de conexión a la base de datos'}), 500
    
    try:
        medicos = Medico.search(search_term)
        return jsonify({'medicos': medicos})
    
    except Exception as e:
        return jsonify({'error': 'Error al buscar médicos'}), 500
    
    finally:
        db.disconnect()