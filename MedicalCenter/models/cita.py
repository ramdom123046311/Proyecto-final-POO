from .database import db
from datetime import datetime, date, time, timedelta

class Cita:
    def __init__(self):
        pass
    
    @staticmethod
    def get_all():
        query = """SELECT c.id_cita, c.id_paciente, c.id_medico, c.fecha, c.hora, c.motivo, c.estatus, c.estado,
                          p.nombres as paciente_nombres, p.apellidos as paciente_apellidos,
                          m.primer_nombre as medico_primer_nombre, m.segundo_nombre as medico_segundo_nombre,
                          m.apellido_paterno as medico_apellido_paterno, m.apellido_materno as medico_apellido_materno, 
                          m.especialidad
                   FROM cita c
                   JOIN pacientes p ON c.id_paciente = p.id_paciente AND p.estatus = 1
                   JOIN medicos m ON c.id_medico = m.id_medico AND m.estatus = 1
                   ORDER BY c.fecha DESC, c.hora DESC"""
        
        result = db.execute_query(query)
        
        citas = []
        if result:
            for cita_data in result:
                # Convertir timedelta a formato de hora legible
                hora_formateada = str(cita_data[4]) if cita_data[4] else ''
                if isinstance(cita_data[4], timedelta):
                    total_seconds = int(cita_data[4].total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    hora_formateada = f"{hours:02d}:{minutes:02d}"
                
                citas.append({
                    'id_cita': cita_data[0],
                    'id_paciente': cita_data[1],
                    'id_medico': cita_data[2],
                    'fecha_cita': cita_data[3],
                    'hora_cita': hora_formateada,
                    'motivo_consulta': cita_data[5],
                    'estatus': cita_data[6],
                    'estado': cita_data[7],
                    'paciente_nombre_completo': f"{cita_data[8]} {cita_data[9]}".strip(),
                    'medico_nombre_completo': f"{cita_data[10] or ''} {cita_data[11] or ''} {cita_data[12]} {cita_data[13] or ''}".strip(),
                    'especialidad': cita_data[14]
                })
        return citas
    
    @staticmethod
    def get_by_id(cita_id):
        """BUGG FATAL"""
        query = """SELECT c.*, 
                          p.nombres as paciente_nombres, p.apellidos as paciente_apellidos, p.fecha_nacimiento,
                          m.primer_nombre as medico_primer_nombre, m.segundo_nombre as medico_segundo_nombre,
                          m.apellido_paterno as medico_apellido_paterno, m.apellido_materno as medico_apellido_materno, 
                          m.especialidad
                   FROM cita c
                   JOIN pacientes p ON c.id_paciente = p.id_paciente AND p.estatus = 1
                   JOIN medicos m ON c.id_medico = m.id_medico AND m.estatus = 1
                   WHERE c.id_cita = %s"""
        
        result = db.execute_query(query, (cita_id,))
        
        if result:
            cita_data = result[0]
            return {
                'id_cita': cita_data[0],
                'id_paciente': cita_data[1],
                'id_medico': cita_data[2],
                'fecha_cita': cita_data[3],
                'hora_cita': cita_data[4],
                'motivo_consulta': cita_data[5],
                'estado': cita_data[6],
                'fecha_creacion': cita_data[7],
                'paciente_nombre_completo': f"{cita_data[8]} {cita_data[9]}".strip(),
                'fecha_nacimiento': cita_data[10],
                'medico_nombre_completo': f"{cita_data[11] or ''} {cita_data[12] or ''} {cita_data[13]} {cita_data[14] or ''}".strip(),
                'especialidad': cita_data[15]
            }
        return None
    
    @staticmethod
    def create(paciente_id, medico_id, fecha, hora, motivo):
        """Crea una nueva cita"""
        query = """INSERT INTO cita (id_paciente, id_medico, fecha, hora, motivo, estatus, estado)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        
        estatus = 'activa'
        estado = 1
        
        result = db.execute_update(query, (paciente_id, medico_id, fecha, hora, 
                                         motivo, estatus, estado))
        
        if result > 0:
            return db.get_last_insert_id()
        return None
    
    @staticmethod
    def update(cita_id, paciente_id, medico_id, fecha, hora, motivo):
        """Actualiza una cita existente"""
        query = """UPDATE cita SET id_paciente = %s, id_medico = %s, fecha = %s, 
                   hora = %s, motivo = %s WHERE id_cita = %s"""
        
        return db.execute_update(query, (paciente_id, medico_id, fecha, hora, 
                                       motivo, cita_id)) > 0
    
    @staticmethod
    def cancel(cita_id):
        """Cancela una cita"""
        query = "UPDATE cita SET estado = 'cancelada' WHERE id_cita = %s"
        return db.execute_update(query, (cita_id,)) > 0
    
    @staticmethod
    def complete(cita_id):
        """Marca una cita como completada"""
        query = "UPDATE cita SET estado = 'completada' WHERE id_cita = %s"
        return db.execute_update(query, (cita_id,)) > 0
    
    @staticmethod
    def delete(cita_id):
        """Elimina una cita"""
        query = "DELETE FROM cita WHERE id_cita = %s"
        return db.execute_update(query, (cita_id,)) > 0
    
    @staticmethod
    def get_by_patient(paciente_id):
        """Obtiene todas las citas de un paciente"""
        query = """SELECT c.*, 
                          m.primer_nombre as medico_primer_nombre, m.segundo_nombre as medico_segundo_nombre,
                          m.apellido_paterno as medico_apellido_paterno, m.apellido_materno as medico_apellido_materno, 
                          m.especialidad
                   FROM cita c
                   JOIN medicos m ON c.id_medico = m.id_medico
                   WHERE c.id_paciente = %s
                   ORDER BY c.fecha DESC, c.hora DESC"""
        
        result = db.execute_query(query, (paciente_id,))
        
        citas = []
        if result:
            for cita_data in result:
                citas.append({
                    'id_cita': cita_data[0],
                    'id_paciente': cita_data[1],
                    'id_medico': cita_data[2],
                    'fecha_cita': cita_data[3],
                    'hora_cita': cita_data[4],
                    'motivo_consulta': cita_data[5],
                    'estado': cita_data[6],
                    'fecha_creacion': cita_data[7],
                    'medico_nombre_completo': f"{cita_data[8] or ''} {cita_data[9] or ''} {cita_data[10]} {cita_data[11] or ''}".strip(),
                    'especialidad': cita_data[12]
                })
        return citas
    
    @staticmethod
    def get_by_doctor(medico_id):
        """Obtiene todas las citas de un médico"""
        query = """SELECT c.*, 
                          p.nombres as paciente_nombres, p.apellidos as paciente_apellidos
                   FROM cita c
                   JOIN pacientes p ON c.id_paciente = p.id_paciente AND p.estatus = 1
                   WHERE c.id_medico = %s
                   ORDER BY c.fecha DESC, c.hora DESC"""
        
        result = db.execute_query(query, (medico_id,))
        
        citas = []
        if result:
            for cita_data in result:
                citas.append({
                    'id_cita': cita_data[0],
                    'id_paciente': cita_data[1],
                    'id_medico': cita_data[2],
                    'fecha_cita': cita_data[3],
                    'hora_cita': cita_data[4],
                    'motivo_consulta': cita_data[5],
                    'estado': cita_data[6],
                    'fecha_creacion': cita_data[7],
                    'paciente_nombre_completo': f"{cita_data[8]} {cita_data[9]}".strip()
                })
        return citas
    
    @staticmethod
    def validate_data(paciente_id, medico_id, fecha_cita, hora_cita, motivo_consulta, cita_id=None):
        """Valida los datos de la cita"""
        errors = []
        
        # Validar campos requeridos
        if not paciente_id:
            errors.append("Debe seleccionar un paciente")
        
        if not medico_id:
            errors.append("Debe seleccionar un médico")
        
        if not fecha_cita:
            errors.append("La fecha de la cita es requerida")
        else:
            try:
                fecha_obj = datetime.strptime(fecha_cita, '%Y-%m-%d').date()
                if fecha_obj < date.today():
                    errors.append("La fecha de la cita no puede ser anterior a hoy")
            except ValueError:
                errors.append("Formato de fecha inválido")
        
        if not hora_cita:
            errors.append("La hora de la cita es requerida")
        else:
            try:
                datetime.strptime(hora_cita, '%H:%M')
            except ValueError:
                errors.append("Formato de hora inválido")
        
        if not motivo_consulta or not motivo_consulta.strip():
            errors.append("El motivo de consulta es requerido")
        elif len(motivo_consulta.strip()) < 10:
            errors.append("El motivo de consulta debe tener al menos 10 caracteres")
        
        # Validar disponibilidad del médico
        if paciente_id and medico_id and fecha_cita and hora_cita:
            if Cita.check_doctor_availability(medico_id, fecha_cita, hora_cita, cita_id):
                errors.append("El médico ya tiene una cita programada en esa fecha y hora")
        
        return errors
    
    @staticmethod
    def check_doctor_availability(medico_id, fecha_cita, hora_cita, exclude_cita_id=None):
        """Verifica si el médico está disponible en la fecha y hora especificada"""
        if exclude_cita_id:
            query = """SELECT COUNT(*) FROM cita WHERE id_medico = %s AND fecha_cita = %s AND hora_cita = %s 
                       AND estado != 'cancelada' AND id_cita != %s"""
            result = db.execute_query(query, (medico_id, fecha_cita, hora_cita, exclude_cita_id))
        else:
            query = """SELECT COUNT(*) FROM cita WHERE id_medico = %s AND fecha_cita = %s AND hora_cita = %s 
                       AND estado != 'cancelada'"""
            result = db.execute_query(query, (medico_id, fecha_cita, hora_cita))
        
        return result and result[0][0] > 0
    
    @staticmethod
    def get_upcoming_appointments(limit=10):
        """Obtiene las próximas citas programadas"""
        query = """SELECT c.*, 
                          p.nombres as paciente_nombres, p.apellidos as paciente_apellidos,
                          m.primer_nombre as medico_primer_nombre, m.segundo_nombre as medico_segundo_nombre,
                          m.apellido_paterno as medico_apellido_paterno, m.apellido_materno as medico_apellido_materno
                   FROM cita c
                   JOIN pacientes p ON c.id_paciente = p.id_paciente AND p.estatus = 1
                   JOIN medicos m ON c.id_medico = m.id_medico AND m.estatus = 1
                   WHERE c.estado = 1 AND c.fecha >= CURDATE()
                   ORDER BY c.fecha ASC, c.hora ASC
                   LIMIT %s"""
        
        result = db.execute_query(query, (limit,))
        
        citas = []
        if result:
            for cita_data in result:
                citas.append({
                    'id_cita': cita_data[0],
                    'id_paciente': cita_data[1],
                    'id_medico': cita_data[2],
                    'fecha_cita': cita_data[4],
                    'hora_cita': cita_data[5],
                    'motivo_consulta': cita_data[6],
                    'estatus': cita_data[7],
                    'paciente_nombre_completo': f"{cita_data[8]} {cita_data[9]}".strip(),
                    'medico_nombre_completo': f"{cita_data[10] or ''} {cita_data[11] or ''} {cita_data[12]} {cita_data[13] or ''}".strip()
                })
        return citas