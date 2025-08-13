from .database import db
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os

class Exploracion:
    def __init__(self):
        pass
    
    @staticmethod
    def get_all():
        """Obtiene todas las exploraciones con información de paciente y médico"""
        query = """SELECT e.*, 
                          p.nombres as paciente_nombres, p.apellidos as paciente_apellidos,
                          m.primer_nombre as medico_primer_nombre, m.segundo_nombre as medico_segundo_nombre,
                          m.apellido_paterno as medico_apellido_paterno, m.apellido_materno as medico_apellido_materno, 
                          m.especialidad
                   FROM exploracion e
                   JOIN pacientes p ON e.id_paciente = p.id_paciente AND p.estatus = 1
                   JOIN medicos m ON e.id_medico = m.id_medico AND m.estatus = 1
                   WHERE e.estatus = 1
                   ORDER BY e.fecha DESC"""
        
        result = db.execute_query(query)
        
        exploraciones = []
        if result:
            for exp_data in result:
                exploraciones.append({
                    'id_exploracion': exp_data[0],
                    'id_paciente': exp_data[1],
                    'id_medico': exp_data[2],
                    'fecha': exp_data[3],
                    'peso': exp_data[4],
                    'altura': exp_data[5],
                    'temperatura': exp_data[6],
                    'latidos_minuto': exp_data[7],
                    'saturacion_oxigeno': exp_data[8],
                    'sintomas': exp_data[9],
                    'diagnostico': exp_data[10],
                    'tratamiento': exp_data[11],
                    'observaciones': exp_data[12],
                    'eliminado': exp_data[13],
                    'paciente_nombre_completo': exp_data[14],
                    'medico_nombre_completo': f"{exp_data[15]} {exp_data[16] or ''} {exp_data[17]} {exp_data[18] or ''}".strip(),
                    'especialidad': exp_data[19]
                })
        return exploraciones
    
    @staticmethod
    def get_by_id(exploracion_id):
        """Obtiene una exploración por su ID con información completa"""
        query = """SELECT e.id_exploracion, e.id_cita, e.id_paciente, e.id_medico, e.fecha, 
                          e.peso, e.altura, e.temperatura, e.latidos_minuto, e.saturacion_oxigeno, 
                          e.glucosa, e.sintomas, e.diagnostico, e.tratamiento, e.estudios, e.estatus,
                          p.nombres as paciente_nombres, p.apellidos as paciente_apellidos, 
                          p.fecha_nacimiento, p.genero,
                          m.primer_nombre as medico_primer_nombre, m.segundo_nombre as medico_segundo_nombre,
                          m.apellido_paterno as medico_apellido_paterno, m.apellido_materno as medico_apellido_materno, 
                          m.especialidad, m.cedula_profesional
                   FROM exploracion e
                   JOIN pacientes p ON e.id_paciente = p.id_paciente AND p.estatus = 1
                   JOIN medicos m ON e.id_medico = m.id_medico AND m.estatus = 1
                   WHERE e.id_exploracion = %s AND e.estatus = 1"""
        
        result = db.execute_query(query, (exploracion_id,))
        
        if result:
            exp_data = result[0]
            return {
                'id_exploracion': exp_data[0],
                'id_cita': exp_data[1],
                'id_paciente': exp_data[2],
                'id_medico': exp_data[3],
                'fecha': exp_data[4],
                'peso': exp_data[5],
                'altura': exp_data[6],
                'temperatura': exp_data[7],
                'latidos_minuto': exp_data[8],
                'saturacion_oxigeno': exp_data[9],
                'glucosa': exp_data[10],
                'sintomas': exp_data[11],
                'diagnostico': exp_data[12],
                'tratamiento': exp_data[13],
                'estudios': exp_data[14],
                'estatus': exp_data[15],
                'paciente_nombre_completo': f"{exp_data[16]} {exp_data[17]}".strip(),
                'paciente_fecha_nacimiento': exp_data[18],
                'paciente_genero': exp_data[19],
                'medico_nombre_completo': f"{exp_data[20]} {exp_data[21] or ''} {exp_data[22]} {exp_data[23] or ''}".strip(),
                'especialidad': exp_data[24],
                'cedula_profesional': exp_data[25]
            }
        return None
    
    @staticmethod
    def create(paciente_id, medico_id, fecha_exploracion, peso, altura, temperatura, 
               latidos_minuto, saturacion_oxigeno, glucosa, sintomas, diagnostico, tratamiento, estudios):
        """Crea una nueva exploración"""
        query = """INSERT INTO exploracion (id_paciente, id_medico, fecha, peso, altura, 
                    temperatura, latidos_minuto, saturacion_oxigeno, glucosa, sintomas, diagnostico, 
                    tratamiento, estudios, estatus)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        
        result = db.execute_update(query, (paciente_id, medico_id, fecha_exploracion, peso, altura,
                                         temperatura, latidos_minuto, saturacion_oxigeno, glucosa, sintomas,
                                         diagnostico, tratamiento, estudios, 1))
        
        if result > 0:
            return db.get_last_insert_id()
        return None
    
    @staticmethod
    def update(exploracion_id, paciente_id, medico_id, fecha_exploracion, peso, altura, temperatura,
               latidos_minuto, saturacion_oxigeno, glucosa, sintomas, diagnostico, tratamiento, estudios):
        """Actualiza una exploración existente"""
        query = """UPDATE exploracion SET id_paciente = %s, id_medico = %s, fecha = %s,
                   peso = %s, altura = %s, temperatura = %s, latidos_minuto = %s, 
                   saturacion_oxigeno = %s, glucosa = %s, sintomas = %s, diagnostico = %s, 
                   tratamiento = %s, estudios = %s WHERE id_exploracion = %s"""
        
        return db.execute_update(query, (paciente_id, medico_id, fecha_exploracion, peso, altura,
                                       temperatura, latidos_minuto, saturacion_oxigeno, glucosa, sintomas,
                                       diagnostico, tratamiento, estudios, exploracion_id)) > 0
    
    @staticmethod
    def soft_delete(exploracion_id):
        """Marca una exploración como eliminada (soft delete)"""
        query = "UPDATE exploracion SET eliminado = 1 WHERE id_exploracion = %s"
        return db.execute_update(query, (exploracion_id,)) > 0
    
    @staticmethod
    def get_by_patient(paciente_id):
        """Obtiene todas las exploraciones de un paciente"""
        query = """SELECT e.*, 
                          m.nombre as medico_nombre, m.apellido_paterno as medico_apellido_paterno,
                          m.apellido_materno as medico_apellido_materno, m.especialidad
                   FROM exploracion e
                   JOIN medicos m ON e.id_medico = m.id_medico
                   WHERE e.id_paciente = %s AND e.estatus = 1
                   ORDER BY e.fecha DESC"""
        
        result = db.execute_query(query, (paciente_id,))
        
        exploraciones = []
        if result:
            for exp_data in result:
                exploraciones.append({
                    'id_exploracion': exp_data[0],
                    'id_paciente': exp_data[1],
                    'id_medico': exp_data[2],
                    'fecha': exp_data[3],
                    'peso': exp_data[4],
                    'altura': exp_data[5],
                    'temperatura': exp_data[6],
                    'latidos_minuto': exp_data[7],
                    'saturacion_oxigeno': exp_data[8],
                    'sintomas': exp_data[9],
                    'diagnostico': exp_data[10],
                    'tratamiento': exp_data[11],
                    'observaciones': exp_data[12],
                    'medico_nombre_completo': f"{exp_data[14]} {exp_data[15]} {exp_data[16] or ''}".strip(),
                    'especialidad': exp_data[17]
                })
        return exploraciones
    
    @staticmethod
    def validate_data(paciente_id, medico_id, fecha_exploracion, peso, altura, temperatura,
                     latidos_minuto, saturacion_oxigeno, glucosa, sintomas, diagnostico, tratamiento, estudios):
        """Valida los datos de la exploración"""
        errors = []
        
        # Validar campos requeridos
        if not paciente_id:
            errors.append("Debe seleccionar un paciente")
        
        if not medico_id:
            errors.append("Debe seleccionar un médico")
        
        if not fecha_exploracion:
            errors.append("La fecha de exploración es requerida")
        else:
            try:
                datetime.strptime(fecha_exploracion, '%Y-%m-%d')
            except ValueError:
                errors.append("Formato de fecha inválido")
        
        # Validar signos vitales
        if peso:
            try:
                peso_float = float(peso)
                if peso_float <= 0 or peso_float > 500:
                    errors.append("El peso debe estar entre 0.1 y 500 kg")
            except ValueError:
                errors.append("El peso debe ser un número válido")
        
        if altura:
            try:
                altura_float = float(altura)
                if altura_float <= 0 or altura_float > 3:
                    errors.append("La altura debe estar entre 0.1 y 3 metros")
            except ValueError:
                errors.append("La altura debe ser un número válido")
        
        if temperatura:
            try:
                temp_float = float(temperatura)
                if temp_float < 30 or temp_float > 45:
                    errors.append("La temperatura debe estar entre 30 y 45 grados Celsius")
            except ValueError:
                errors.append("La temperatura debe ser un número válido")
        
        if latidos_minuto:
            try:
                lm_int = int(latidos_minuto)
                if lm_int < 30 or lm_int > 200:
                    errors.append("Los latidos por minuto deben estar entre 30 y 200 bpm")
            except ValueError:
                errors.append("Los latidos por minuto deben ser un número entero válido")
        
        if saturacion_oxigeno:
            try:
                so_float = float(saturacion_oxigeno)
                if so_float < 70 or so_float > 100:
                    errors.append("La saturación de oxígeno debe estar entre 70 y 100%")
            except ValueError:
                errors.append("La saturación de oxígeno debe ser un número válido")
        
        if glucosa:
            try:
                glucosa_float = float(glucosa)
                if glucosa_float < 50 or glucosa_float > 500:
                    errors.append("La glucosa debe estar entre 50 y 500 mg/dL")
            except ValueError:
                errors.append("La glucosa debe ser un número válido")
        
        # Validar campos de texto
        if not sintomas or not sintomas.strip():
            errors.append("Los síntomas son requeridos")
        elif len(sintomas.strip()) < 10:
            errors.append("Los síntomas deben tener al menos 10 caracteres")
        
        if not diagnostico or not diagnostico.strip():
            errors.append("El diagnóstico es requerido")
        elif len(diagnostico.strip()) < 10:
            errors.append("El diagnóstico debe tener al menos 10 caracteres")
        
        if not tratamiento or not tratamiento.strip():
            errors.append("El tratamiento es requerido")
        elif len(tratamiento.strip()) < 10:
            errors.append("El tratamiento debe tener al menos 10 caracteres")
        
        return errors
    
    @staticmethod
    def generate_medical_report(exploracion_id):
        """Genera un reporte médico en PDF"""
        print(f"DEBUG: Iniciando generación de PDF para exploración {exploracion_id}")
        exploracion = Exploracion.get_by_id(exploracion_id)
        print(f"DEBUG: Datos de exploración obtenidos: {exploracion is not None}")
        if not exploracion:
            print("DEBUG: No se encontró la exploración")
            return None
        
        # Crear directorio de reportes si no existe
        reports_dir = 'static/reports'
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        
        # Nombre del archivo
        filename = f"reporte_medico_{exploracion_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(reports_dir, filename)
        
        # Crear el documento PDF
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        # Título
        story.append(Paragraph("RECETA MÉDICA", title_style))
        story.append(Spacer(1, 20))
        
        # Información del paciente
        story.append(Paragraph("INFORMACIÓN DEL PACIENTE", heading_style))
        patient_data = [
            ['Nombre:', exploracion['paciente_nombre_completo']],
            ['Fecha de Nacimiento:', str(exploracion['paciente_fecha_nacimiento'])],
            ['Género:', 'Masculino' if exploracion['paciente_genero'] == 'M' else 'Femenino'],
            ['Fecha de Exploración:', str(exploracion['fecha'])]
        ]
        
        patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
        patient_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(patient_table)
        story.append(Spacer(1, 20))
        
        # Información del médico
        story.append(Paragraph("INFORMACIÓN DEL MÉDICO", heading_style))
        doctor_data = [
            ['Nombre:', exploracion['medico_nombre_completo']],
            ['Especialidad:', exploracion['especialidad']],
            ['Cédula Profesional:', exploracion['cedula_profesional']]
        ]
        
        doctor_table = Table(doctor_data, colWidths=[2*inch, 4*inch])
        doctor_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(doctor_table)
        story.append(Spacer(1, 20))
        
        # Signos vitales
        story.append(Paragraph("SIGNOS VITALES", heading_style))
        vitals_data = [
            ['Peso:', f"{exploracion['peso']} kg" if exploracion['peso'] else 'No registrado'],
            ['Altura:', f"{exploracion['altura']} m" if exploracion['altura'] else 'No registrado'],
            ['Temperatura:', f"{exploracion['temperatura']} °C" if exploracion['temperatura'] else 'No registrado'],
            ['Saturación de Oxígeno:', f"{exploracion['saturacion_oxigeno']}%" if exploracion['saturacion_oxigeno'] else 'No registrado'],
            ['Frecuencia Cardíaca:', f"{exploracion['latidos_minuto']} bpm" if exploracion['latidos_minuto'] else 'No registrado'],
            ['Glucosa:', f"{exploracion['glucosa']} mg/dL" if exploracion['glucosa'] else 'No registrado']
        ]
        
        vitals_table = Table(vitals_data, colWidths=[2*inch, 4*inch])
        vitals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(vitals_table)
        story.append(Spacer(1, 20))
        
        # Síntomas
        story.append(Paragraph("SÍNTOMAS", heading_style))
        story.append(Paragraph(exploracion['sintomas'], styles['Normal']))
        story.append(Spacer(1, 15))
        
        # Diagnóstico
        story.append(Paragraph("DIAGNÓSTICO", heading_style))
        story.append(Paragraph(exploracion['diagnostico'], styles['Normal']))
        story.append(Spacer(1, 15))
        
        # Tratamiento
        story.append(Paragraph("TRATAMIENTO", heading_style))
        story.append(Paragraph(exploracion['tratamiento'], styles['Normal']))
        story.append(Spacer(1, 15))
        
        # Estudios solicitados
        if exploracion['estudios']:
            story.append(Paragraph("ESTUDIOS SOLICITADOS", heading_style))
            story.append(Paragraph(exploracion['estudios'], styles['Normal']))
            story.append(Spacer(1, 15))
        
        # Generar el PDF
        doc.build(story)
        print(f"DEBUG: PDF generado en: {filepath}")
        
        return filepath