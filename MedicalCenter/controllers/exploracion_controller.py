from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from models import Exploracion, Paciente, Medico
from controllers.auth_controller import login_required
import mysql.connector
import tempfile
import os

exploracion_bp = Blueprint('exploracion', __name__)

@exploracion_bp.route('/exploraciones')
@login_required
def exploraciones():
    """Página principal de exploraciones"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='medicalcenter',
            user='root',
            password='admin',
            buffered=True
        )
        cursor = connection.cursor(dictionary=True)
        
        # Obtener todas las exploraciones
        cursor.execute("""
            SELECT e.id_exploracion, e.id_cita, e.fecha,
                   CONCAT(p.nombres, ' ', p.apellidos) as nombre_paciente,
                   CONCAT(m.primer_nombre, ' ', m.apellido_paterno) as nombre_medico
            FROM exploracion e
            JOIN cita c ON e.id_cita = c.id_cita
            JOIN pacientes p ON c.id_paciente = p.id_paciente
            JOIN medicos m ON c.id_medico = m.id_medico
            ORDER BY e.fecha DESC
        """)
        exploraciones = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return render_template('gestion_exploraciones.html', exploraciones=exploraciones)
    
    except Exception as e:
        flash('Error al cargar las exploraciones', 'error')
        return render_template('gestion_exploraciones.html', exploraciones=[])

@exploracion_bp.route('/exploracion/<int:cita_id>', methods=['GET'])
def exploracion(cita_id):
    """Ruta principal para exploración - verifica si existe y redirige o muestra formulario"""
    print(f"DEBUG: Accediendo a exploracion con cita_id: {cita_id}")
    
    # Primera conexión: verificar si existe exploración
    try:
        conn1 = mysql.connector.connect(
            host='localhost',
            database='medicalcenter',
            user='root',
            password='admin',
            buffered=True
        )
        cursor1 = conn1.cursor(dictionary=True)
        cursor1.execute("SELECT id_exploracion FROM exploracion WHERE id_cita = %s", (cita_id,))
        exploracion_existente = cursor1.fetchone()
        cursor1.close()
        conn1.close()
        print(f"DEBUG: Exploración existente: {exploracion_existente}")
        
        if exploracion_existente:
            print(f"DEBUG: Redirigiendo a editar_exploracion con id: {exploracion_existente['id_exploracion']}")
            return redirect(url_for('exploracion.editar_exploracion', exploracion_id=exploracion_existente['id_exploracion']))
    except Exception as e:
        print(f"DEBUG: Error verificando exploración existente: {str(e)}")
        flash('Error al verificar exploración', 'error')
        return redirect(url_for('cita.citas'))
    
    # Segunda conexión: obtener datos de la cita
    try:
        conn2 = mysql.connector.connect(
            host='localhost',
            database='medicalcenter',
            user='root',
            password='admin',
            buffered=True
        )
        cursor2 = conn2.cursor(dictionary=True)
        cursor2.execute("""
            SELECT C.id_cita, C.id_paciente, C.id_medico, 
                   P.nombres AS nombres_paciente, P.apellidos AS apellidos_paciente, 
                   P.fecha_nacimiento, 
                   CONCAT(M.primer_nombre, ' ', M.apellido_paterno) AS nombre_medico
            FROM cita C
            JOIN pacientes P ON C.id_paciente = P.id_paciente
            JOIN medicos M ON C.id_medico = M.id_medico
            WHERE C.id_cita = %s
        """, (cita_id,))
        cita = cursor2.fetchone()
        cursor2.close()
        conn2.close()
        
        if not cita:
            print("DEBUG: Cita no encontrada")
            flash('Cita no encontrada', 'error')
            return redirect(url_for('cita.citas'))
        
        # Calcular edad del paciente
        from datetime import datetime
        fecha_nacimiento = cita['fecha_nacimiento']
        hoy = datetime.now().date()
        edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
        
        print(f"DEBUG: Renderizando template con cita: {cita['nombres_paciente']} {cita['apellidos_paciente']}")
        return render_template('exploracion.html', cita=cita, edad=edad, fecha_actual=hoy.strftime('%d/%m/%Y'))
        
    except Exception as e:
        print(f"DEBUG: Error obteniendo datos de cita: {str(e)}")
        flash('Error al procesar la solicitud', 'error')
        return redirect(url_for('cita.citas'))

@exploracion_bp.route('/nueva_exploracion', methods=['GET', 'POST'])
@login_required
def nueva_exploracion():
    """Crear nueva exploración"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            paciente_id = request.form.get('paciente_id')
            medico_id = request.form.get('medico_id')
            fecha_exploracion = request.form.get('fecha')
            peso = request.form.get('peso')
            altura = request.form.get('altura')
            presion_arterial = request.form.get('presion_arterial', '').strip()
            frecuencia_cardiaca = request.form.get('frecuencia_cardiaca')
            temperatura = request.form.get('temperatura')
            sintomas = request.form.get('sintomas', '').strip()
            diagnostico = request.form.get('diagnostico', '').strip()
            tratamiento = request.form.get('tratamiento', '').strip()
            observaciones = request.form.get('observaciones', '').strip()
            
            # Validar campos requeridos
            if not all([paciente_id, medico_id, fecha_exploracion]):
                flash('Paciente, médico y fecha de exploración son requeridos', 'error')
                return redirect(url_for('exploracion.nueva_exploracion'))
            
            # Conectar a la base de datos
            if not db.connect():
                flash('Error de conexión a la base de datos', 'error')
                return redirect(url_for('exploracion.nueva_exploracion'))
            
            # Crear la exploración
            success = Exploracion.create(
                paciente_id=int(paciente_id),
                medico_id=int(medico_id),
                fecha_exploracion=fecha_exploracion,
                peso=float(peso) if peso else None,
                altura=float(altura) if altura else None,
                presion_arterial=presion_arterial,
                frecuencia_cardiaca=int(frecuencia_cardiaca) if frecuencia_cardiaca else None,
                temperatura=float(temperatura) if temperatura else None,
                sintomas=sintomas,
                diagnostico=diagnostico,
                tratamiento=tratamiento,
                observaciones=observaciones
            )
            
            if success:
                flash('Exploración creada exitosamente', 'success')
                return redirect(url_for('exploracion.exploraciones'))
            else:
                flash('Error al crear la exploración', 'error')
                return redirect(url_for('exploracion.nueva_exploracion'))
        
        except Exception as e:
            flash('Error al procesar la exploración', 'error')
            return redirect(url_for('exploracion.nueva_exploracion'))
        
        finally:
            db.disconnect()
    
    # GET request - mostrar formulario
    if not db.connect():
        flash('Error de conexión a la base de datos', 'error')
        return render_template('exploracion.html', pacientes=[], medicos=[])
    
    try:
        pacientes = Paciente.get_all()
        medicos = Medico.get_all()
        return render_template('exploracion.html', pacientes=pacientes, medicos=medicos)
    
    except Exception as e:
        flash('Error al cargar los datos', 'error')
        return render_template('exploracion.html', pacientes=[], medicos=[])
    
    finally:
        db.disconnect()

@exploracion_bp.route('/editar_exploracion/<int:exploracion_id>', methods=['GET', 'POST'])
def editar_exploracion(exploracion_id):
    """Editar una exploración existente"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='medicalcenter',
            user='root',
            password='admin',
            buffered=True
        )
        cursor = connection.cursor(dictionary=True)
        
        if request.method == 'POST':
            # Obtener datos del formulario
            datos = {
                'peso': request.form.get('peso'),
                'altura': request.form.get('altura'),
                'temperatura': request.form.get('temperatura'),
                'latidos_minuto': request.form.get('latidos_minuto'),
                'saturacion_oxigeno': request.form.get('saturacion_oxigeno'),
                'glucosa': request.form.get('glucosa'),
                'sintomas': request.form.get('sintomas'),
                'diagnostico': request.form.get('diagnostico'),
                'tratamiento': request.form.get('tratamiento'),
                'estudios': request.form.get('estudios'),
            }
            
            # Actualizar exploración
            cursor.execute("""
                UPDATE exploracion SET
                    peso = %s, altura = %s, temperatura = %s, 
                    latidos_minuto = %s, saturacion_oxigeno = %s, glucosa = %s,
                    sintomas = %s, diagnostico = %s, tratamiento = %s, estudios = %s
                WHERE id_exploracion = %s
            """, (
                datos['peso'], datos['altura'], datos['temperatura'], 
                datos['latidos_minuto'], datos['saturacion_oxigeno'], datos['glucosa'],
                datos['sintomas'], datos['diagnostico'], datos['tratamiento'], 
                datos['estudios'], exploracion_id
            ))
            
            connection.commit()
            cursor.close()
            connection.close()
            
            # Generar y descargar PDF automáticamente
            try:
                print(f"DEBUG: Intentando generar PDF para exploración {exploracion_id}")
                pdf_path = Exploracion.generate_medical_report(exploracion_id)
                print(f"DEBUG: PDF path generado: {pdf_path}")
                if pdf_path and os.path.exists(pdf_path):
                    print(f"DEBUG: PDF existe, enviando archivo: {pdf_path}")
                    return send_file(pdf_path, as_attachment=True, download_name=f'exploracion_{exploracion_id}.pdf')
                else:
                    print(f"DEBUG: PDF no existe o path es None: {pdf_path}")
                    flash('Exploración actualizada pero error al generar PDF', 'warning')
                    return redirect(url_for('exploracion.ver_exploracion', exploracion_id=exploracion_id))
            except Exception as e:
                print(f"Error al generar PDF: {str(e)}")
                import traceback
                traceback.print_exc()
                flash('Exploración actualizada pero error al generar PDF', 'warning')
                return redirect(url_for('exploracion.ver_exploracion', exploracion_id=exploracion_id))
        
        # GET request - obtener datos de la exploración
        cursor.execute("""
            SELECT E.*, 
                   CONCAT(P.nombres, ' ', P.apellidos) AS nombre_paciente,
                   CONCAT(M.primer_nombre, ' ', M.apellido_paterno) AS nombre_medico,
                   P.fecha_nacimiento
            FROM exploracion E
            JOIN pacientes P ON E.id_paciente = P.id_paciente
            JOIN medicos M ON E.id_medico = M.id_medico
            WHERE E.id_exploracion = %s
        """, (exploracion_id,))
        exploracion = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if not exploracion:
            flash('Exploración no encontrada', 'error')
            return redirect(url_for('exploracion.exploraciones'))
        
        # Calcular edad del paciente en el momento de la exploración
        fecha_exploracion = exploracion['fecha']
        fecha_nac = exploracion['fecha_nacimiento']
        if fecha_exploracion and fecha_nac:
            edad = fecha_exploracion.year - fecha_nac.year - ((fecha_exploracion.month, fecha_exploracion.day) < (fecha_nac.month, fecha_nac.day))
        else:
            edad = 0
        
        return render_template('editar_exploracion.html', exploracion=exploracion, edad=edad)
        
    except Exception as e:
        print(f"ERROR en editar_exploracion: {str(e)}")
        flash('Error al procesar la solicitud', 'error')
        return redirect(url_for('exploracion.exploraciones'))

@exploracion_bp.route('/crear_exploracion/<int:cita_id>', methods=['POST'])
def crear_exploracion(cita_id):
    """Crear nueva exploración y generar PDF automáticamente"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='medicalcenter',
            user='root',
            password='admin',
            buffered=True
        )
        cursor = connection.cursor(dictionary=True)
        
        datos = {
            'peso': request.form.get('peso'),
            'altura': request.form.get('altura'),
            'temperatura': request.form.get('temperatura'),
            'latidos_minuto': request.form.get('latidos_minuto'),
            'saturacion_oxigeno': request.form.get('saturacion_oxigeno'),
            'glucosa': request.form.get('glucosa'),
            'sintomas': request.form.get('sintomas'),
            'diagnostico': request.form.get('diagnostico'),
            'tratamiento': request.form.get('tratamiento'),
            'estudios': request.form.get('estudios'),
        }
        cursor.execute("SELECT id_paciente, id_medico FROM cita WHERE id_cita = %s", (cita_id,))
        cita = cursor.fetchone()

        if not cita:
            flash('Cita no encontrada', 'error')
            cursor.close()
            connection.close()
            return redirect(url_for('cita.citas'))

        id_paciente, id_medico = cita['id_paciente'], cita['id_medico']

        cursor.execute("""
            INSERT INTO exploracion (
                id_cita, id_paciente, id_medico, fecha,
                peso, altura, temperatura, latidos_minuto, saturacion_oxigeno, glucosa,
                sintomas, diagnostico, tratamiento, estudios, estatus
            ) VALUES (%s, %s, %s, CURDATE(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
        """, (
            cita_id, id_paciente, id_medico,
            datos['peso'], datos['altura'], datos['temperatura'], datos['latidos_minuto'],
            datos['saturacion_oxigeno'], datos['glucosa'], datos['sintomas'],
            datos['diagnostico'], datos['tratamiento'], datos['estudios']
        ))

        connection.commit()
        id_exploracion = cursor.lastrowid
        cursor.close()
        connection.close()

        # Generar PDF automáticamente
        pdf_path = Exploracion.generate_medical_report(id_exploracion)
        if pdf_path and os.path.exists(pdf_path):
            return send_file(pdf_path, as_attachment=True, download_name=f'reporte_exploracion_{id_exploracion}.pdf')
        else:
            flash('Exploración creada pero error al generar PDF', 'warning')
            return redirect(url_for('exploracion.exploraciones'))
            
    except Exception as e:
        print(f"Error al crear exploración: {str(e)}")
        flash('Error al crear la exploración', 'error')
        return redirect(url_for('cita.citas'))

@exploracion_bp.route('/nueva_exploracion_desde_cita/<int:cita_id>', methods=['GET', 'POST'])
def nueva_exploracion_desde_cita(cita_id):
    """Crear nueva exploración desde una cita"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            peso = request.form.get('peso')
            altura = request.form.get('altura')
            presion_arterial = request.form.get('presion_arterial', '').strip()
            frecuencia_cardiaca = request.form.get('frecuencia_cardiaca')
            temperatura = request.form.get('temperatura')
            saturacion_oxigeno = request.form.get('saturacion_oxigeno')
            glucosa = request.form.get('glucosa')
            sintomas = request.form.get('sintomas', '').strip()
            diagnostico = request.form.get('diagnostico', '').strip()
            tratamiento = request.form.get('tratamiento', '').strip()
            estudios_solicitados = request.form.get('estudios_solicitados', '').strip()
            
            # Conectar a la base de datos
            connection = mysql.connector.connect(
                host='localhost',
                database='medicalcenter',
                user='root',
                password='admin',
                buffered=True
            )
            
            # Crear la exploración usando el método create_from_cita
            exploracion_id = Exploracion.create_from_cita(
                id_cita=cita_id,
                peso=float(peso) if peso else None,
                altura=float(altura) if altura else None,
                presion_arterial=presion_arterial,
                frecuencia_cardiaca=int(frecuencia_cardiaca) if frecuencia_cardiaca else None,
                temperatura=float(temperatura) if temperatura else None,
                saturacion_oxigeno=int(saturacion_oxigeno) if saturacion_oxigeno else None,
                glucosa=float(glucosa) if glucosa else None,
                sintomas=sintomas,
                diagnostico=diagnostico,
                tratamiento=tratamiento,
                estudios_solicitados=estudios_solicitados
            )
            
            if exploracion_id:
                flash('Exploración creada exitosamente', 'success')
                return redirect(url_for('exploracion.exploraciones'))
            else:
                flash('Error al crear la exploración', 'error')
                return redirect(url_for('exploracion.nueva_exploracion_desde_cita', cita_id=cita_id))
        
        except Exception as e:
            flash('Error al procesar la exploración', 'error')
            return redirect(url_for('exploracion.nueva_exploracion_desde_cita', cita_id=cita_id))
        
        finally:
            if 'connection' in locals():
                connection.close()
    
    # GET request - mostrar formulario
    from models.cita import Cita
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='medicalcenter',
            user='root',
            password='admin',
            buffered=True
        )
    except Exception as e:
        flash('Error de conexión a la base de datos', 'error')
        return redirect(url_for('cita.citas'))
    
    try:
        cita = Cita.get_by_id(cita_id)
        if not cita:
            flash('Cita no encontrada', 'error')
            return redirect(url_for('cita.citas'))
        
        # Calcular edad del paciente
        from datetime import datetime
        if cita['fecha_nacimiento']:
            fecha_nacimiento = datetime.strptime(str(cita['fecha_nacimiento']), '%Y-%m-%d')
            edad = datetime.now().year - fecha_nacimiento.year
            if datetime.now().month < fecha_nacimiento.month or (datetime.now().month == fecha_nacimiento.month and datetime.now().day < fecha_nacimiento.day):
                edad -= 1
        else:
            edad = None
        
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        
        return render_template('exploracion.html', 
                             cita=cita, 
                             edad=edad, 
                             fecha_actual=fecha_actual)
    
    except Exception as e:
        print(f"Error en nueva_exploracion_desde_cita: {str(e)}")
        flash(f'Error al cargar los datos de la cita: {str(e)}', 'error')
        return redirect(url_for('cita.citas'))
    
    finally:
        db.disconnect()

@exploracion_bp.route('/eliminar_exploracion/<int:exploracion_id>', methods=['POST'])
@login_required
def eliminar_exploracion(exploracion_id):
    """Eliminar exploración (soft delete)"""
    if not db.connect():
        flash('Error de conexión a la base de datos', 'error')
        return redirect(url_for('exploracion.exploraciones'))
    
    try:
        success = Exploracion.soft_delete(exploracion_id)
        
        if success:
            flash('Exploración eliminada exitosamente', 'success')
        else:
            flash('Error al eliminar la exploración', 'error')
    
    except Exception as e:
        flash('Error al procesar la eliminación', 'error')
    
    finally:
        db.disconnect()
    
    return redirect(url_for('exploracion.exploraciones'))

@exploracion_bp.route('/ver_exploracion/<int:exploracion_id>')
@login_required
def ver_exploracion(exploracion_id):
    """Ver detalles de la exploración"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='medicalcenter',
            user='root',
            password='admin',
            buffered=True
        )
        cursor = connection.cursor(dictionary=True)
        
        # Obtener datos de la exploración con información del paciente y médico
        cursor.execute("""
            SELECT E.*, 
                   CONCAT(P.nombres, ' ', P.apellidos) AS nombre_paciente,
                   CONCAT(M.primer_nombre, ' ', M.apellido_paterno) AS nombre_medico,
                   P.fecha_nacimiento
            FROM exploracion E
            JOIN pacientes P ON E.id_paciente = P.id_paciente
            JOIN medicos M ON E.id_medico = M.id_medico
            WHERE E.id_exploracion = %s
        """, (exploracion_id,))
        exploracion = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if not exploracion:
            flash('Exploración no encontrada', 'error')
            return redirect(url_for('exploracion.exploraciones'))
        
        # Calcular edad del paciente en el momento de la exploración
        fecha_exploracion = exploracion['fecha']
        fecha_nac = exploracion['fecha_nacimiento']
        if fecha_exploracion and fecha_nac:
            edad = fecha_exploracion.year - fecha_nac.year - ((fecha_exploracion.month, fecha_exploracion.day) < (fecha_nac.month, fecha_nac.day))
        else:
            edad = 0
        
        return render_template('ver_exploracion.html', exploracion=exploracion, edad=edad)
    
    except Exception as e:
        print(f"ERROR en ver_exploracion: {str(e)}")
        flash('Error al cargar los datos de la exploración', 'error')
        return redirect(url_for('exploracion.exploraciones'))

@exploracion_bp.route('/generar_pdf/<int:exploracion_id>')
@login_required
def generar_pdf(exploracion_id):
    """Generar PDF de la exploración"""
    if not db.connect():
        flash('Error de conexión a la base de datos', 'error')
        return redirect(url_for('exploracion.exploraciones'))
    
    try:
        # Generar el PDF
        pdf_path = Exploracion.generate_medical_report(exploracion_id)
        
        if pdf_path and os.path.exists(pdf_path):
            return send_file(pdf_path, as_attachment=True, download_name=f'exploracion_{exploracion_id}.pdf')
        else:
            flash('Error al generar el PDF', 'error')
            return redirect(url_for('exploracion.exploraciones'))
    
    except Exception as e:
        flash('Error al generar el PDF', 'error')
        return redirect(url_for('exploracion.exploraciones'))
    
    finally:
        db.disconnect()

@exploracion_bp.route('/api/exploraciones_paciente/<int:paciente_id>')
@login_required
def api_exploraciones_paciente(paciente_id):
    """API para obtener exploraciones de un paciente"""
    if not db.connect():
        return jsonify({'error': 'Error de conexión a la base de datos'}), 500
    
    try:
        exploraciones = Exploracion.get_by_patient(paciente_id)
        return jsonify({'exploraciones': exploraciones})
    
    except Exception as e:
        return jsonify({'error': 'Error al obtener las exploraciones'}), 500
    
    finally:
        db.disconnect()

@exploracion_bp.route('/api/exploraciones_medico/<int:medico_id>')
@login_required
def api_exploraciones_medico(medico_id):
    """API para obtener exploraciones de un médico"""
    if not db.connect():
        return jsonify({'error': 'Error de conexión a la base de datos'}), 500
    
    try:
        exploraciones = Exploracion.get_by_doctor(medico_id)
        return jsonify({'exploraciones': exploraciones})
    
    except Exception as e:
        return jsonify({'error': 'Error al obtener las exploraciones'}), 500
    
    finally:
        db.disconnect()