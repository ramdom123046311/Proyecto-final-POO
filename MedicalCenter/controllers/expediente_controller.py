from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models import Expediente, Paciente, Medico, Exploracion, db
from controllers.auth_controller import login_required

expediente_bp = Blueprint('expediente', __name__)

@expediente_bp.route('/expedientes')
@login_required
def expedientes():
    """Página principal de expedientes"""
    if not db.connect():
        flash('Error de conexión a la base de datos', 'error')
        return render_template('expedientes.html', expedientes=[])
    
    try:
        # Obtener término de búsqueda si existe
        search_term = request.args.get('search', '').strip()
        
        if search_term:
            expedientes = Expediente.search(search_term)
        else:
            expedientes = Expediente.get_all()
        
        return render_template('expedientes.html', expedientes=expedientes, search_term=search_term)
    
    except Exception as e:
        flash('Error al cargar los expedientes', 'error')
        return render_template('expedientes.html', expedientes=[])
    
    finally:
        db.disconnect()

@expediente_bp.route('/nuevo_expediente', methods=['GET', 'POST'])
@login_required
def nuevo_expediente():
    """Crear nuevo expediente"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            paciente_id = request.form.get('paciente_id')
            medico_id = request.form.get('medico_id')
            exploracion_id = request.form.get('exploracion_id')
            fecha_creacion = request.form.get('fecha_creacion')
            diagnostico_principal = request.form.get('diagnostico_principal', '').strip()
            diagnosticos_secundarios = request.form.get('diagnosticos_secundarios', '').strip()
            tratamiento_recomendado = request.form.get('tratamiento_recomendado', '').strip()
            medicamentos_prescritos = request.form.get('medicamentos_prescritos', '').strip()
            observaciones_medicas = request.form.get('observaciones_medicas', '').strip()
            recomendaciones = request.form.get('recomendaciones', '').strip()
            
            # Validar campos requeridos
            if not all([paciente_id, medico_id, exploracion_id, fecha_creacion, diagnostico_principal]):
                flash('Paciente, médico, exploración, fecha de creación y diagnóstico principal son requeridos', 'error')
                return redirect(url_for('expediente.nuevo_expediente'))
            
            # Conectar a la base de datos
            if not db.connect():
                flash('Error de conexión a la base de datos', 'error')
                return redirect(url_for('expediente.nuevo_expediente'))
            
            # Crear el expediente
            success = Expediente.create(
                paciente_id=int(paciente_id),
                medico_id=int(medico_id),
                exploracion_id=int(exploracion_id),
                fecha_creacion=fecha_creacion,
                diagnostico_principal=diagnostico_principal,
                diagnosticos_secundarios=diagnosticos_secundarios,
                tratamiento_recomendado=tratamiento_recomendado,
                medicamentos_prescritos=medicamentos_prescritos,
                observaciones_medicas=observaciones_medicas,
                recomendaciones=recomendaciones
            )
            
            if success:
                flash('Expediente creado exitosamente', 'success')
                return redirect(url_for('expediente.expedientes'))
            else:
                flash('Error al crear el expediente', 'error')
                return redirect(url_for('expediente.nuevo_expediente'))
        
        except Exception as e:
            flash('Error al procesar el expediente', 'error')
            return redirect(url_for('expediente.nuevo_expediente'))
        
        finally:
            db.disconnect()
    
    # GET request - mostrar formulario
    if not db.connect():
        flash('Error de conexión a la base de datos', 'error')
        return render_template('expedientes.html', pacientes=[], medicos=[], exploraciones=[])
    
    try:
        pacientes = Paciente.get_all()
        medicos = Medico.get_all()
        exploraciones = Exploracion.get_all()
        return render_template('expedientes.html', 
                             pacientes=pacientes, 
                             medicos=medicos, 
                             exploraciones=exploraciones)
    
    except Exception as e:
        flash('Error al cargar los datos', 'error')
        return render_template('expedientes.html', pacientes=[], medicos=[], exploraciones=[])
    
    finally:
        db.disconnect()

@expediente_bp.route('/editar_expediente/<int:expediente_id>', methods=['GET', 'POST'])
@login_required
def editar_expediente(expediente_id):
    """Editar expediente existente"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            paciente_id = request.form.get('paciente_id')
            medico_id = request.form.get('medico_id')
            exploracion_id = request.form.get('exploracion_id')
            fecha_creacion = request.form.get('fecha_creacion')
            diagnostico_principal = request.form.get('diagnostico_principal', '').strip()
            diagnosticos_secundarios = request.form.get('diagnosticos_secundarios', '').strip()
            tratamiento_recomendado = request.form.get('tratamiento_recomendado', '').strip()
            medicamentos_prescritos = request.form.get('medicamentos_prescritos', '').strip()
            observaciones_medicas = request.form.get('observaciones_medicas', '').strip()
            recomendaciones = request.form.get('recomendaciones', '').strip()
            
            # Validar campos requeridos
            if not all([paciente_id, medico_id, exploracion_id, fecha_creacion, diagnostico_principal]):
                flash('Paciente, médico, exploración, fecha de creación y diagnóstico principal son requeridos', 'error')
                return redirect(url_for('expediente.editar_expediente', expediente_id=expediente_id))
            
            # Conectar a la base de datos
            if not db.connect():
                flash('Error de conexión a la base de datos', 'error')
                return redirect(url_for('expediente.editar_expediente', expediente_id=expediente_id))
            
            # Actualizar el expediente
            success = Expediente.update(
                expediente_id=expediente_id,
                paciente_id=int(paciente_id),
                medico_id=int(medico_id),
                exploracion_id=int(exploracion_id),
                fecha_creacion=fecha_creacion,
                diagnostico_principal=diagnostico_principal,
                diagnosticos_secundarios=diagnosticos_secundarios,
                tratamiento_recomendado=tratamiento_recomendado,
                medicamentos_prescritos=medicamentos_prescritos,
                observaciones_medicas=observaciones_medicas,
                recomendaciones=recomendaciones
            )
            
            if success:
                flash('Expediente actualizado exitosamente', 'success')
                return redirect(url_for('expediente.expedientes'))
            else:
                flash('Error al actualizar el expediente', 'error')
                return redirect(url_for('expediente.editar_expediente', expediente_id=expediente_id))
        
        except Exception as e:
            flash('Error al procesar la actualización', 'error')
            return redirect(url_for('expediente.editar_expediente', expediente_id=expediente_id))
        
        finally:
            db.disconnect()
    
    # GET request - mostrar formulario de edición
    if not db.connect():
        flash('Error de conexión a la base de datos', 'error')
        return redirect(url_for('expediente.expedientes'))
    
    try:
        expediente = Expediente.get_by_id(expediente_id)
        if not expediente:
            flash('Expediente no encontrado', 'error')
            return redirect(url_for('expediente.expedientes'))
        
        pacientes = Paciente.get_all()
        medicos = Medico.get_all()
        exploraciones = Exploracion.get_all()
        
        return render_template('editar_expediente.html', 
                             expediente=expediente,
                             pacientes=pacientes, 
                             medicos=medicos, 
                             exploraciones=exploraciones)
    
    except Exception as e:
        flash('Error al cargar los datos', 'error')
        return redirect(url_for('expediente.expedientes'))
    
    finally:
        db.disconnect()

@expediente_bp.route('/eliminar_expediente/<int:expediente_id>', methods=['POST'])
@login_required
def eliminar_expediente(expediente_id):
    """Eliminar expediente"""
    if not db.connect():
        flash('Error de conexión a la base de datos', 'error')
        return redirect(url_for('expediente.expedientes'))
    
    try:
        success = Expediente.delete(expediente_id)
        
        if success:
            flash('Expediente eliminado exitosamente', 'success')
        else:
            flash('Error al eliminar el expediente', 'error')
    
    except Exception as e:
        flash('Error al procesar la eliminación', 'error')
    
    finally:
        db.disconnect()
    
    return redirect(url_for('expediente.expedientes'))

@expediente_bp.route('/ver_expediente/<int:expediente_id>')
@login_required
def ver_expediente(expediente_id):
    """Ver detalles del expediente"""
    if not db.connect():
        flash('Error de conexión a la base de datos', 'error')
        return redirect(url_for('expediente.expedientes'))
    
    try:
        expediente = Expediente.get_by_id(expediente_id)
        if not expediente:
            flash('Expediente no encontrado', 'error')
            return redirect(url_for('expediente.expedientes'))
        
        return render_template('ver_expediente.html', expediente=expediente)
    
    except Exception as e:
        flash('Error al cargar los datos del expediente', 'error')
        return redirect(url_for('expediente.expedientes'))
    
    finally:
        db.disconnect()

@expediente_bp.route('/api/expedientes_paciente/<int:paciente_id>')
@login_required
def api_expedientes_paciente(paciente_id):
    """API para obtener expedientes de un paciente"""
    if not db.connect():
        return jsonify({'error': 'Error de conexión a la base de datos'}), 500
    
    try:
        expedientes = Expediente.get_by_patient(paciente_id)
        return jsonify({'expedientes': expedientes})
    
    except Exception as e:
        return jsonify({'error': 'Error al obtener los expedientes'}), 500
    
    finally:
        db.disconnect()

@expediente_bp.route('/api/expedientes_medico/<int:medico_id>')
@login_required
def api_expedientes_medico(medico_id):
    """API para obtener expedientes de un médico"""
    if not db.connect():
        return jsonify({'error': 'Error de conexión a la base de datos'}), 500
    
    try:
        expedientes = Expediente.get_by_doctor(medico_id)
        return jsonify({'expedientes': expedientes})
    
    except Exception as e:
        return jsonify({'error': 'Error al obtener los expedientes'}), 500
    
    finally:
        db.disconnect()

@expediente_bp.route('/api/buscar_expedientes')
@login_required
def api_buscar_expedientes():
    """API para buscar expedientes"""
    search_term = request.args.get('q', '').strip()
    
    if not search_term:
        return jsonify({'expedientes': []})
    
    if not db.connect():
        return jsonify({'error': 'Error de conexión a la base de datos'}), 500
    
    try:
        expedientes = Expediente.search(search_term)
        return jsonify({'expedientes': expedientes})
    
    except Exception as e:
        return jsonify({'error': 'Error al buscar expedientes'}), 500
    
    finally:
        db.disconnect()