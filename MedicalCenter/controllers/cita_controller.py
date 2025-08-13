from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models import Cita, Paciente, Medico, db
from controllers.auth_controller import login_required
from datetime import datetime

cita_bp = Blueprint('cita', __name__)

@cita_bp.route('/citas')
@login_required
def citas():
    """Página principal de citas"""
    if not db.connect():
        flash('Error de conexión a la base de datos', 'error')
        return render_template('citas.html', citas=[], pacientes=[], medicos=[])
    
    try:
        # Obtener todas las citas
        citas = Cita.get_all()
        
        # Obtener pacientes y médicos para los formularios
        pacientes = Paciente.get_all()
        medicos = Medico.get_all()
        
        return render_template('citas.html', citas=citas, pacientes=pacientes, medicos=medicos)
    
    except Exception as e:
        print(f"ERROR EN CITAS: {str(e)}")
        print(f"TIPO DE ERROR: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        flash(f'Error al cargar los datos: {str(e)}', 'error')
        return render_template('citas.html', citas=[], pacientes=[], medicos=[])
    
    finally:
        db.disconnect()

@cita_bp.route('/nueva_cita', methods=['GET', 'POST'])
@login_required
def nueva_cita():
    """Crear nueva cita"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            paciente_id = request.form.get('paciente_id')
            medico_id = request.form.get('medico_id')
            fecha = request.form.get('fecha')
            hora = request.form.get('hora')
            motivo = request.form.get('motivo', '').strip()
            
            # Validaciones del servidor
            errores = {}
            
            if not paciente_id:
                errores['paciente_id'] = 'El paciente es requerido'
            else:
                try:
                    paciente_id = int(paciente_id)
                except ValueError:
                    errores['paciente_id'] = 'ID de paciente inválido'
            
            if not medico_id:
                errores['medico_id'] = 'El médico es requerido'
            else:
                try:
                    medico_id = int(medico_id)
                except ValueError:
                    errores['medico_id'] = 'ID de médico inválido'
            
            if not fecha:
                errores['fecha'] = 'La fecha es requerida'
            else:
                try:
                    fecha_cita = datetime.strptime(fecha, '%Y-%m-%d')
                    if fecha_cita.date() < datetime.now().date():
                        errores['fecha'] = 'La fecha de la cita no puede ser en el pasado'
                except ValueError:
                    errores['fecha'] = 'Formato de fecha inválido'
            
            if not hora:
                errores['hora'] = 'La hora es requerida'
            else:
                try:
                    # Validar formato de hora
                    datetime.strptime(hora, '%H:%M')
                    # Si es el mismo día, validar que la hora no sea pasada
                    if fecha and fecha == datetime.now().strftime('%Y-%m-%d'):
                        hora_cita = datetime.strptime(f"{fecha} {hora}", '%Y-%m-%d %H:%M')
                        if hora_cita < datetime.now():
                            errores['hora'] = 'La hora de la cita no puede ser en el pasado'
                except ValueError:
                    errores['hora'] = 'Formato de hora inválido (HH:MM)'
            
            if errores:
                for campo, mensaje in errores.items():
                    flash(mensaje, 'error')
                return redirect(url_for('cita.nueva_cita'))
            
            # Conectar a la base de datos
            if not db.connect():
                flash('Error de conexión a la base de datos', 'error')
                return redirect(url_for('cita.nueva_cita'))
            
            # Crear la cita
            success = Cita.create(
                paciente_id=int(paciente_id),
                medico_id=int(medico_id),
                fecha=fecha,
                hora=hora,
                motivo=motivo
            )
            
            if success:
                flash('Cita creada exitosamente', 'success')
                return redirect(url_for('cita.citas'))
            else:
                flash('Error al crear la cita', 'error')
                return redirect(url_for('cita.nueva_cita'))
        
        except Exception as e:
            flash('Error al procesar la cita', 'error')
            return redirect(url_for('cita.nueva_cita'))
        
        finally:
            db.disconnect()
    
    # GET request - mostrar formulario
    if not db.connect():
        flash('Error de conexión a la base de datos', 'error')
        return render_template('citas.html', citas=[], pacientes=[], medicos=[])
    
    try:
        citas = Cita.get_upcoming_appointments()
        pacientes = Paciente.get_all()
        medicos = Medico.get_all()
        return render_template('citas.html', citas=citas, pacientes=pacientes, medicos=medicos)
    
    except Exception as e:
        print(f"ERROR EN NUEVA_CITA: {str(e)}")
        print(f"TIPO DE ERROR: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        flash(f'Error al cargar los datos: {str(e)}', 'error')
        return render_template('citas.html', citas=[], pacientes=[], medicos=[])
    
    finally:
        db.disconnect()

@cita_bp.route('/editar_cita/<int:cita_id>', methods=['GET', 'POST'])
@login_required
def editar_cita(cita_id):
    """Editar cita existente"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            paciente_id = request.form.get('paciente_id')
            medico_id = request.form.get('medico_id')
            fecha = request.form.get('fecha')
            hora = request.form.get('hora')
            motivo = request.form.get('motivo', '').strip()
            estado = request.form.get('estado', 'programada')
            
            # Validaciones del servidor
            errores = {}
            
            if not paciente_id:
                errores['paciente_id'] = 'El paciente es requerido'
            else:
                try:
                    paciente_id = int(paciente_id)
                except ValueError:
                    errores['paciente_id'] = 'ID de paciente inválido'
            
            if not medico_id:
                errores['medico_id'] = 'El médico es requerido'
            else:
                try:
                    medico_id = int(medico_id)
                except ValueError:
                    errores['medico_id'] = 'ID de médico inválido'
            
            if not fecha:
                errores['fecha'] = 'La fecha es requerida'
            else:
                try:
                    fecha_cita = datetime.strptime(fecha, '%Y-%m-%d')
                    if fecha_cita.date() < datetime.now().date():
                        errores['fecha'] = 'La fecha de la cita no puede ser en el pasado'
                except ValueError:
                    errores['fecha'] = 'Formato de fecha inválido'
            
            if not hora:
                errores['hora'] = 'La hora es requerida'
            else:
                try:
                    # Validar formato de hora
                    datetime.strptime(hora, '%H:%M')
                    # Si es el mismo día, validar que la hora no sea pasada
                    if fecha and fecha == datetime.now().strftime('%Y-%m-%d'):
                        hora_cita = datetime.strptime(f"{fecha} {hora}", '%Y-%m-%d %H:%M')
                        if hora_cita < datetime.now():
                            errores['hora'] = 'La hora de la cita no puede ser en el pasado'
                except ValueError:
                    errores['hora'] = 'Formato de hora inválido (HH:MM)'
            
            if errores:
                for campo, mensaje in errores.items():
                    flash(mensaje, 'error')
                return redirect(url_for('cita.editar_cita', cita_id=cita_id))
            
            # Conectar a la base de datos
            if not db.connect():
                flash('Error de conexión a la base de datos', 'error')
                return redirect(url_for('cita.editar_cita', cita_id=cita_id))
            
            # Actualizar la cita
            fecha_hora = f"{fecha} {hora}"
            success = Cita.update(
                cita_id=cita_id,
                paciente_id=int(paciente_id),
                medico_id=int(medico_id),
                fecha_hora=fecha_hora,
                motivo=motivo,
                estado=estado
            )
            
            if success:
                flash('Cita actualizada exitosamente', 'success')
                return redirect(url_for('cita.citas'))
            else:
                flash('Error al actualizar la cita', 'error')
                return redirect(url_for('cita.editar_cita', cita_id=cita_id))
        
        except Exception as e:
            flash('Error al procesar la actualización', 'error')
            return redirect(url_for('cita.editar_cita', cita_id=cita_id))
        
        finally:
            db.disconnect()
    
    # GET request - mostrar formulario de edición
    if not db.connect():
        flash('Error de conexión a la base de datos', 'error')
        return redirect(url_for('cita.citas'))
    
    try:
        cita = Cita.get_by_id(cita_id)
        if not cita:
            flash('Cita no encontrada', 'error')
            return redirect(url_for('cita.citas'))
        
        citas = Cita.get_upcoming_appointments()
        pacientes = Paciente.get_all()
        medicos = Medico.get_all()
        
        return render_template('citas.html', 
                             citas=citas,
                             pacientes=pacientes, 
                             medicos=medicos,
                             modo_edicion=True,
                             form_data=cita)
    
    except Exception as e:
        flash('Error al cargar los datos', 'error')
        return redirect(url_for('cita.citas'))
    
    finally:
        db.disconnect()

@cita_bp.route('/eliminar_cita/<int:cita_id>', methods=['POST'])
@login_required
def eliminar_cita(cita_id):
    """Eliminar cita"""
    if not db.connect():
        flash('Error de conexión a la base de datos', 'error')
        return redirect(url_for('cita.citas'))
    
    try:
        success = Cita.delete(cita_id)
        
        if success:
            flash('Cita eliminada exitosamente', 'success')
        else:
            flash('Error al eliminar la cita', 'error')
    
    except Exception as e:
        flash('Error al procesar la eliminación', 'error')
    
    finally:
        db.disconnect()
    
    return redirect(url_for('cita.citas'))

@cita_bp.route('/api/citas_paciente/<int:paciente_id>')
@login_required
def api_citas_paciente(paciente_id):
    """API para obtener citas de un paciente"""
    if not db.connect():
        return jsonify({'error': 'Error de conexión a la base de datos'}), 500
    
    try:
        citas = Cita.get_by_patient(paciente_id)
        return jsonify({'citas': citas})
    
    except Exception as e:
        return jsonify({'error': 'Error al obtener las citas'}), 500
    
    finally:
        db.disconnect()

@cita_bp.route('/iniciar_exploracion/<int:cita_id>')
@login_required
def iniciar_exploracion(cita_id):
    """Iniciar exploración desde una cita"""
    if not db.connect():
        flash('Error de conexión a la base de datos', 'error')
        return redirect(url_for('cita.citas'))
    
    try:
        # Obtener información de la cita
        cita = Cita.get_by_id(cita_id)
        if not cita:
            flash('Cita no encontrada', 'error')
            return redirect(url_for('cita.citas'))
        
        # Calcular edad del paciente
        from datetime import datetime
        if cita.get('fecha_nacimiento'):
            fecha_nacimiento = datetime.strptime(str(cita['fecha_nacimiento']), '%Y-%m-%d')
            edad = (datetime.now() - fecha_nacimiento).days // 365
        else:
            edad = 'N/A'
        
        # Fecha actual
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        
        return render_template('exploracion.html', 
                             cita=cita, 
                             edad=edad, 
                             fecha_actual=fecha_actual)
    
    except Exception as e:
        flash('Error al cargar los datos de la cita', 'error')
        return redirect(url_for('cita.citas'))
    
    finally:
        db.disconnect()

@cita_bp.route('/api/citas_medico/<int:medico_id>')
@login_required
def api_citas_medico(medico_id):
    """API para obtener citas de un médico"""
    if not db.connect():
        return jsonify({'error': 'Error de conexión a la base de datos'}), 500
    
    try:
        citas = Cita.get_by_doctor(medico_id)
        return jsonify({'citas': citas})
    
    except Exception as e:
        return jsonify({'error': 'Error al obtener las citas'}), 500
    
    finally:
        db.disconnect()