from .database import db
from datetime import datetime
import re

class Medico:
    def __init__(self):
        pass
    
    @staticmethod
    def get_all():
        """Obtiene todos los médicos activos"""
        query = "SELECT * FROM medicos WHERE estatus = 1 ORDER BY primer_nombre, apellido_paterno"
        result = db.execute_query(query)
        
        medicos = []
        if result:
            for medico_data in result:
                medicos.append({
                    'id_medico': medico_data[0],
                    'primer_nombre': medico_data[1],
                    'segundo_nombre': medico_data[2],
                    'apellido_paterno': medico_data[3],
                    'apellido_materno': medico_data[4],
                    'cedula_profesional': medico_data[5],
                    'especialidad': medico_data[6],
                    'correo': medico_data[7],
                    'rfc': medico_data[8],
                    'telefono': medico_data[9],
                    'centro_medico': medico_data[10],
                    'estatus': medico_data[11],
                    'nombre_completo': f"{medico_data[1] or ''} {medico_data[2] or ''} {medico_data[3]} {medico_data[4] or ''}".strip(),
                    'contrasena': medico_data[12]
                })
        return medicos
    
    @staticmethod
    def get_by_id(medico_id):
        """Obtiene un médico por su ID"""
        query = "SELECT * FROM medicos WHERE id_medico = %s"
        result = db.execute_query(query, (medico_id,))
        
        if result:
            medico_data = result[0]
            return {
                'id_medico': medico_data[0],
                'primer_nombre': medico_data[1],
                'segundo_nombre': medico_data[2],
                'apellido_paterno': medico_data[3],
                'apellido_materno': medico_data[4],
                'cedula_profesional': medico_data[5],
                'especialidad': medico_data[6],
                'correo': medico_data[7],
                'rfc': medico_data[8],
                'telefono': medico_data[9],
                'centro_medico': medico_data[10],
                'estatus': medico_data[11],
                'contrasena': medico_data[12]
            }
        return None
    
    @staticmethod
    def create(primer_nombre, segundo_nombre, apellido_paterno, apellido_materno, especialidad, 
               cedula_profesional, correo, rfc, telefono, centro_medico, contrasena):
        """Crea un nuevo médico"""
        try:
            # Primero crear el usuario en la tabla usuarios
            import hashlib
            contrasena_hash = hashlib.sha256(contrasena.encode()).hexdigest()
            
            user_query = """INSERT INTO usuarios (rfc, contrasena, privilegio, estatus) 
                           VALUES (%s, %s, %s, %s)"""
            
            user_result = db.execute_update(user_query, (rfc, contrasena_hash, 1, 1))
            
            if user_result > 0:
                # Luego crear el médico
                medico_query = """INSERT INTO medicos (primer_nombre, segundo_nombre, apellido_paterno, apellido_materno, 
                                 cedula_profesional, especialidad, correo, rfc, telefono, centro_medico, estatus, contrasena)
                                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                
                medico_result = db.execute_update(medico_query, (primer_nombre, segundo_nombre, apellido_paterno, apellido_materno,
                                                 cedula_profesional, especialidad, correo, rfc, telefono, 
                                                 centro_medico, 1, contrasena_hash))
                
                if medico_result > 0:
                    return db.get_last_insert_id()
            
            return None
        except Exception as e:
            print(f"Error creando médico: {e}")
            return None
    
    @staticmethod
    def update(medico_id, primer_nombre, segundo_nombre, apellido_paterno, apellido_materno, 
               especialidad, cedula_profesional, correo, rfc, telefono, centro_medico):
        """Actualiza un médico existente"""
        query = """UPDATE medicos SET primer_nombre = %s, segundo_nombre = %s, apellido_paterno = %s, 
                   apellido_materno = %s, especialidad = %s, cedula_profesional = %s, correo = %s,
                   rfc = %s, telefono = %s, centro_medico = %s WHERE id_medico = %s"""
        
        return db.execute_update(query, (primer_nombre, segundo_nombre, apellido_paterno, apellido_materno,
                                       especialidad, cedula_profesional, correo, rfc, telefono,
                                       centro_medico, medico_id)) > 0
    
    @staticmethod
    def delete(medico_id):
        """Elimina un médico"""
        query = "DELETE FROM medicos WHERE id_medico = %s"
        return db.execute_update(query, (medico_id,)) > 0
    
    @staticmethod
    def search(search_term):
        """Busca médicos por nombre, apellido o especialidad"""
        query = """SELECT * FROM medicos WHERE 
                   primer_nombre LIKE %s OR segundo_nombre LIKE %s OR apellido_paterno LIKE %s OR 
                   apellido_materno LIKE %s OR especialidad LIKE %s
                   ORDER BY primer_nombre, apellido_paterno"""
        
        search_pattern = f"%{search_term}%"
        result = db.execute_query(query, (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))
        
        medicos = []
        if result:
            for medico_data in result:
                medicos.append({
                    'id_medico': medico_data[0],
                    'primer_nombre': medico_data[1],
                    'segundo_nombre': medico_data[2],
                    'apellido_paterno': medico_data[3],
                    'apellido_materno': medico_data[4],
                    'cedula_profesional': medico_data[5],
                    'especialidad': medico_data[6],
                    'correo': medico_data[7],
                    'rfc': medico_data[8],
                    'telefono': medico_data[9],
                    'centro_medico': medico_data[10],
                    'estatus': medico_data[11],
                    'contrasena': medico_data[12]
                })
        return medicos
    
    @staticmethod
    def validate_data(nombre, apellido_paterno, apellido_materno, especialidad, cedula_profesional,
                     telefono, email, horario_inicio, horario_fin, medico_id=None):
        """Valida los datos del médico"""
        errors = []
        
        # Validar campos requeridos
        if not nombre or not nombre.strip():
            errors.append("El nombre es requerido")
        elif len(nombre.strip()) < 2:
            errors.append("El nombre debe tener al menos 2 caracteres")
        
        if not apellido_paterno or not apellido_paterno.strip():
            errors.append("El apellido paterno es requerido")
        elif len(apellido_paterno.strip()) < 2:
            errors.append("El apellido paterno debe tener al menos 2 caracteres")
        
        if not especialidad or not especialidad.strip():
            errors.append("La especialidad es requerida")
        elif len(especialidad.strip()) < 3:
            errors.append("La especialidad debe tener al menos 3 caracteres")
        
        if not cedula_profesional or not cedula_profesional.strip():
            errors.append("La cédula profesional es requerida")
        elif not re.match(r'^[0-9]{7,8}$', cedula_profesional.strip()):
            errors.append("La cédula profesional debe tener 7 u 8 dígitos")
        else:
            # Verificar si la cédula ya existe
            if Medico.exists_cedula(cedula_profesional.strip(), medico_id):
                errors.append("La cédula profesional ya está registrada")
        
        if not telefono or not telefono.strip():
            errors.append("El teléfono es requerido")
        elif not re.match(r'^[0-9+\-\s()]{10,15}$', telefono.strip()):
            errors.append("El formato del teléfono no es válido")
        
        if email and email.strip():
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email.strip()):
                errors.append("El formato del email no es válido")
        
        if not horario_inicio:
            errors.append("El horario de inicio es requerido")
        
        if not horario_fin:
            errors.append("El horario de fin es requerido")
        
        if horario_inicio and horario_fin:
            try:
                inicio = datetime.strptime(horario_inicio, '%H:%M').time()
                fin = datetime.strptime(horario_fin, '%H:%M').time()
                if inicio >= fin:
                    errors.append("El horario de inicio debe ser anterior al horario de fin")
            except ValueError:
                errors.append("Formato de horario inválido")
        
        return errors
    
    @staticmethod
    def exists_cedula(cedula_profesional, exclude_id=None):
        """Verifica si una cédula profesional ya existe"""
        if exclude_id:
            query = "SELECT COUNT(*) FROM medicos WHERE cedula_profesional = %s AND id_medico != %s"
            result = db.execute_query(query, (cedula_profesional, exclude_id))
        else:
            query = "SELECT COUNT(*) FROM medicos WHERE cedula_profesional = %s"
            result = db.execute_query(query, (cedula_profesional,))
        
        return result and result[0][0] > 0
    
    @staticmethod
    def get_available_doctors():
        """Obtiene médicos disponibles para citas"""
        query = "SELECT id_medico, primer_nombre, segundo_nombre, apellido_paterno, apellido_materno, especialidad FROM medicos ORDER BY primer_nombre"
        result = db.execute_query(query)
        
        medicos = []
        if result:
            for medico_data in result:
                nombre_completo = f"{medico_data[1]} {medico_data[2] or ''} {medico_data[3]} {medico_data[4] or ''}".strip()
                medicos.append({
                    'id_medico': medico_data[0],
                    'nombre_completo': nombre_completo,
                    'especialidad': medico_data[5]
                })
        return medicos