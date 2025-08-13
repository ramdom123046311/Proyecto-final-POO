from .database import db
from datetime import datetime

class Expediente:
    def __init__(self):
        pass
    
    @staticmethod
    def get_all():
        """Obtiene todos los expedientes con información de paciente y médico"""
        query = """SELECT exp.id, exp.paciente_id, exp.diagnostico, exp.fecha, exp.deleted,
                          p.nombres as paciente_nombres, p.apellidos as paciente_apellidos
                   FROM expedientes exp
                   JOIN pacientes p ON exp.paciente_id = p.id_paciente AND p.estatus = 1
                   WHERE exp.deleted = 0
                   ORDER BY exp.fecha DESC"""
        
        result = db.execute_query(query)
        
        expedientes = []
        if result:
            for exp_data in result:
                expedientes.append({
                    'id': exp_data[0],
                    'paciente_id': exp_data[1],
                    'diagnostico': exp_data[2],
                    'fecha': exp_data[3],
                    'deleted': exp_data[4],
                    'paciente_nombre_completo': f"{exp_data[5]} {exp_data[6]}".strip()
                })
        return expedientes
    
    @staticmethod
    def get_by_id(expediente_id):
        """Obtiene un expediente por su ID con información completa"""
        query = """SELECT exp.id, exp.paciente_id, exp.diagnostico, exp.fecha, exp.deleted,
                          p.nombres as paciente_nombres, p.apellidos as paciente_apellidos, 
                          p.fecha_nacimiento, p.genero, p.tipo_sangre, p.alergias
                   FROM expedientes exp
                   JOIN pacientes p ON exp.paciente_id = p.id_paciente AND p.estatus = 1
                   WHERE exp.id = %s AND exp.deleted = 0"""
        
        result = db.execute_query(query, (expediente_id,))
        
        if result:
            exp_data = result[0]
            return {
                'id': exp_data[0],
                'paciente_id': exp_data[1],
                'diagnostico': exp_data[2],
                'fecha': exp_data[3],
                'deleted': exp_data[4],
                'paciente_nombre_completo': f"{exp_data[5]} {exp_data[6]}".strip(),
                'paciente_fecha_nacimiento': exp_data[7],
                'paciente_genero': exp_data[8],
                'paciente_tipo_sangre': exp_data[9],
                'paciente_alergias': exp_data[10]
            }
        return None
    
    @staticmethod
    def create_from_exploration(exploracion_id, diagnostico_principal=None):
        """Crea un expediente a partir de una exploración"""
        # Obtener información de la exploración
        from .exploracion import Exploracion
        exploracion = Exploracion.get_by_id(exploracion_id)
        
        if not exploracion:
            return None
        
        # Generar número de expediente único
        numero_expediente = Expediente.generate_expediente_number()
        
        # Usar el diagnóstico de la exploración si no se proporciona uno principal
        if not diagnostico_principal:
            diagnostico_principal = exploracion['diagnostico']
        
        query = """INSERT INTO expedientes (paciente_id, medico_id, exploracion_id, numero_expediente, 
                   diagnostico_principal, fecha_creacion)
                   VALUES (%s, %s, %s, %s, %s, %s)"""
        
        fecha_creacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        result = db.execute_update(query, (exploracion['paciente_id'], exploracion['medico_id'],
                                         exploracion_id, numero_expediente, diagnostico_principal,
                                         fecha_creacion))
        
        if result > 0:
            return db.get_last_insert_id()
        return None
    
    @staticmethod
    def create(paciente_id, medico_id, exploracion_id, diagnostico_principal):
        """Crea un nuevo expediente"""
        numero_expediente = Expediente.generate_expediente_number()
        
        query = """INSERT INTO expedientes (paciente_id, medico_id, exploracion_id, numero_expediente,
                   diagnostico_principal, fecha_creacion)
                   VALUES (%s, %s, %s, %s, %s, %s)"""
        
        fecha_creacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        result = db.execute_update(query, (paciente_id, medico_id, exploracion_id, numero_expediente,
                                         diagnostico_principal, fecha_creacion))
        
        if result > 0:
            return db.get_last_insert_id()
        return None
    
    @staticmethod
    def update(expediente_id, diagnostico_principal):
        """Actualiza un expediente existente"""
        query = "UPDATE expedientes SET diagnostico_principal = %s WHERE id = %s"
        return db.execute_update(query, (diagnostico_principal, expediente_id)) > 0
    
    @staticmethod
    def delete(expediente_id):
        """Elimina un expediente"""
        query = "DELETE FROM expedientes WHERE id = %s"
        return db.execute_update(query, (expediente_id,)) > 0
    
    @staticmethod
    def get_by_patient(paciente_id):
        """Obtiene todos los expedientes de un paciente"""
        query = """SELECT exp.*, 
                          m.nombre as medico_nombre, m.apellido_paterno as medico_apellido_paterno,
                          m.apellido_materno as medico_apellido_materno, m.especialidad,
                          e.fecha, e.diagnostico
                   FROM expedientes exp
                   JOIN medicos m ON exp.medico_id = m.id_medico
                   JOIN exploracion e ON exp.exploracion_id = e.id_exploracion
                   WHERE exp.paciente_id = %s
                   ORDER BY exp.fecha_creacion DESC"""
        
        result = db.execute_query(query, (paciente_id,))
        
        expedientes = []
        if result:
            for exp_data in result:
                expedientes.append({
                    'id': exp_data[0],
                    'paciente_id': exp_data[1],
                    'medico_id': exp_data[2],
                    'exploracion_id': exp_data[3],
                    'numero_expediente': exp_data[4],
                    'diagnostico_principal': exp_data[5],
                    'fecha_creacion': exp_data[6],
                    'medico_nombre_completo': f"{exp_data[7]} {exp_data[8]} {exp_data[9] or ''}".strip(),
                    'especialidad': exp_data[10],
                    'fecha_exploracion': exp_data[11],
                    'diagnostico_exploracion': exp_data[12]
                })
        return expedientes
    
    @staticmethod
    def get_by_doctor(medico_id):
        """Obtiene todos los expedientes de un médico"""
        query = """SELECT exp.*, 
                          p.nombre as paciente_nombre, p.apellido_paterno as paciente_apellido_paterno,
                          p.apellido_materno as paciente_apellido_materno,
                          e.fecha, e.diagnostico
                   FROM expedientes exp
                   JOIN pacientes p ON exp.paciente_id = p.id_paciente AND p.estatus = 1
                   JOIN exploracion e ON exp.exploracion_id = e.id_exploracion
                   WHERE exp.medico_id = %s
                   ORDER BY exp.fecha_creacion DESC"""
        
        result = db.execute_query(query, (medico_id,))
        
        expedientes = []
        if result:
            for exp_data in result:
                expedientes.append({
                    'id': exp_data[0],
                    'paciente_id': exp_data[1],
                    'medico_id': exp_data[2],
                    'exploracion_id': exp_data[3],
                    'numero_expediente': exp_data[4],
                    'diagnostico_principal': exp_data[5],
                    'fecha_creacion': exp_data[6],
                    'paciente_nombre_completo': f"{exp_data[7]} {exp_data[8]} {exp_data[9] or ''}".strip(),
                    'fecha_exploracion': exp_data[10],
                    'diagnostico_exploracion': exp_data[11]
                })
        return expedientes
    
    @staticmethod
    def search(search_term):
        """Busca expedientes por número de expediente, nombre de paciente o diagnóstico"""
        query = """SELECT exp.*, 
                          p.nombre as paciente_nombre, p.apellido_paterno as paciente_apellido_paterno, 
                          p.apellido_materno as paciente_apellido_materno,
                          m.nombre as medico_nombre, m.apellido_paterno as medico_apellido_paterno,
                          m.apellido_materno as medico_apellido_materno, m.especialidad
                   FROM expedientes exp
                   JOIN pacientes p ON exp.paciente_id = p.id_paciente AND p.estatus = 1
                   JOIN medicos m ON exp.medico_id = m.id_medico AND m.estatus = 1
                   WHERE exp.numero_expediente LIKE %s OR 
                         p.nombre LIKE %s OR p.apellido_paterno LIKE %s OR p.apellido_materno LIKE %s OR
                         exp.diagnostico_principal LIKE %s
                   ORDER BY exp.fecha_creacion DESC"""
        
        search_pattern = f"%{search_term}%"
        result = db.execute_query(query, (search_pattern, search_pattern, search_pattern, 
                                        search_pattern, search_pattern))
        
        expedientes = []
        if result:
            for exp_data in result:
                expedientes.append({
                    'id': exp_data[0],
                    'paciente_id': exp_data[1],
                    'medico_id': exp_data[2],
                    'exploracion_id': exp_data[3],
                    'numero_expediente': exp_data[4],
                    'diagnostico_principal': exp_data[5],
                    'fecha_creacion': exp_data[6],
                    'paciente_nombre_completo': f"{exp_data[7]} {exp_data[8]} {exp_data[9] or ''}".strip(),
                    'medico_nombre_completo': f"{exp_data[10]} {exp_data[11]} {exp_data[12] or ''}".strip(),
                    'especialidad': exp_data[13]
                })
        return expedientes
    
    @staticmethod
    def generate_expediente_number():
        """Genera un número de expediente único"""
        # Obtener el año actual
        year = datetime.now().year
        
        # Buscar el último número de expediente del año
        query = """SELECT numero_expediente FROM expedientes 
                   WHERE numero_expediente LIKE %s 
                   ORDER BY numero_expediente DESC LIMIT 1"""
        
        pattern = f"{year}-%"
        result = db.execute_query(query, (pattern,))
        
        if result and result[0][0]:
            # Extraer el número secuencial del último expediente
            last_number = result[0][0]
            try:
                sequence = int(last_number.split('-')[1]) + 1
            except (IndexError, ValueError):
                sequence = 1
        else:
            sequence = 1
        
        # Formatear el número con ceros a la izquierda
        return f"{year}-{sequence:04d}"
    
    @staticmethod
    def validate_data(paciente_id, medico_id, exploracion_id, diagnostico_principal):
        """Valida los datos del expediente"""
        errors = []
        
        if not paciente_id:
            errors.append("Debe seleccionar un paciente")
        
        if not medico_id:
            errors.append("Debe seleccionar un médico")
        
        if not exploracion_id:
            errors.append("Debe seleccionar una exploración")
        
        if not diagnostico_principal or not diagnostico_principal.strip():
            errors.append("El diagnóstico principal es requerido")
        elif len(diagnostico_principal.strip()) < 10:
            errors.append("El diagnóstico principal debe tener al menos 10 caracteres")
        
        # Verificar que la exploración no tenga ya un expediente
        if exploracion_id:
            if Expediente.exploration_has_expediente(exploracion_id):
                errors.append("Esta exploración ya tiene un expediente asociado")
        
        return errors
    
    @staticmethod
    def exploration_has_expediente(exploracion_id):
        """Verifica si una exploración ya tiene un expediente asociado"""
        query = "SELECT COUNT(*) FROM expedientes WHERE exploracion_id = %s"
        result = db.execute_query(query, (exploracion_id,))
        return result and result[0][0] > 0
    
    @staticmethod
    def get_recent_expedientes(limit=10):
        """Obtiene los expedientes más recientes"""
        query = """SELECT exp.*, 
                          p.nombre as paciente_nombre, p.apellido_paterno as paciente_apellido_paterno, 
                          p.apellido_materno as paciente_apellido_materno,
                          m.nombre as medico_nombre, m.apellido_paterno as medico_apellido_paterno,
                          m.apellido_materno as medico_apellido_materno
                   FROM expedientes exp
                   JOIN pacientes p ON exp.paciente_id = p.id_paciente AND p.estatus = 1
                   JOIN medicos m ON exp.medico_id = m.id_medico AND m.estatus = 1
                   ORDER BY exp.fecha_creacion DESC
                   LIMIT %s"""
        
        result = db.execute_query(query, (limit,))
        
        expedientes = []
        if result:
            for exp_data in result:
                expedientes.append({
                    'id': exp_data[0],
                    'numero_expediente': exp_data[4],
                    'diagnostico_principal': exp_data[5],
                    'fecha_creacion': exp_data[6],
                    'paciente_nombre_completo': f"{exp_data[7]} {exp_data[8]} {exp_data[9] or ''}".strip(),
                    'medico_nombre_completo': f"{exp_data[10]} {exp_data[11]} {exp_data[12] or ''}".strip()
                })
        return expedientes