from .database import db
from datetime import datetime, date
import re

class Paciente:
    def __init__(self):
        pass
    
    @staticmethod
    def get_all():
        """Obtiene todos los pacientes activos"""
        query = "SELECT * FROM pacientes WHERE estatus = 1 ORDER BY nombres, apellidos"
        result = db.execute_query(query)
        
        pacientes = []
        if result:
            for paciente_data in result:
                pacientes.append({
                    'id_paciente': paciente_data[0],
                    'nombres': paciente_data[1],
                    'apellidos': paciente_data[2],
                    'fecha_nacimiento': paciente_data[3],
                    'genero': paciente_data[4],
                    'tipo_sangre': paciente_data[5],
                    'alergias': paciente_data[6],
                    'estatus': paciente_data[7],
                    'nombre_completo': f"{paciente_data[1]} {paciente_data[2]}".strip()
                })
        return pacientes
    
    @staticmethod
    def get_by_id(paciente_id):
        """Obtiene un paciente por su ID"""
        query = "SELECT * FROM pacientes WHERE id_paciente = %s AND estatus = 1"
        result = db.execute_query(query, (paciente_id,))
        
        if result:
            paciente_data = result[0]
            return {
                'id_paciente': paciente_data[0],
                'nombres': paciente_data[1],
                'apellidos': paciente_data[2],
                'fecha_nacimiento': paciente_data[3],
                'genero': paciente_data[4],
                'tipo_sangre': paciente_data[5],
                'alergias': paciente_data[6],
                'estatus': paciente_data[7]
            }
        return None
    
    @staticmethod
    def create(nombres, apellidos, fecha_nacimiento, genero, tipo_sangre, alergias=None):
        """Crea un nuevo paciente"""
        query = """INSERT INTO pacientes (nombres, apellidos, fecha_nacimiento, genero, tipo_sangre, alergias, estatus) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        
        result = db.execute_update(query, (nombres, apellidos, fecha_nacimiento, genero, tipo_sangre, alergias, 1))
        
        if result > 0:
            return db.get_last_insert_id()
        return None
    
    @staticmethod
    def update(paciente_id, nombres, apellidos, fecha_nacimiento, genero, tipo_sangre, alergias):
        """Actualiza un paciente existente"""
        query = """UPDATE pacientes SET nombres = %s, apellidos = %s, fecha_nacimiento = %s,
                   genero = %s, tipo_sangre = %s, alergias = %s WHERE id_paciente = %s"""
        
        return db.execute_update(query, (nombres, apellidos, fecha_nacimiento, genero, tipo_sangre, alergias, paciente_id)) > 0
    
    @staticmethod
    def delete(paciente_id):
        """Elimina un paciente (soft delete)"""
        query = "UPDATE pacientes SET estatus = 0 WHERE id_paciente = %s"
        return db.execute_update(query, (paciente_id,)) > 0
    
    @staticmethod
    def search(search_term):
        """Busca pacientes por nombre o apellido"""
        query = """SELECT * FROM pacientes WHERE estatus = 1 AND
                   (nombres LIKE %s OR apellidos LIKE %s)
                   ORDER BY nombres, apellidos"""
        
        search_pattern = f"%{search_term}%"
        result = db.execute_query(query, (search_pattern, search_pattern))
        
        pacientes = []
        if result:
            for paciente_data in result:
                pacientes.append({
                    'id_paciente': paciente_data[0],
                    'nombres': paciente_data[1],
                    'apellidos': paciente_data[2],
                    'fecha_nacimiento': paciente_data[3],
                    'genero': paciente_data[4],
                    'tipo_sangre': paciente_data[5],
                    'alergias': paciente_data[6],
                    'estatus': paciente_data[7]
                })
        return pacientes
    
    @staticmethod
    def validate_data(nombre, apellido_paterno, apellido_materno, fecha_nacimiento, genero,
                     telefono, email, direccion, contacto_emergencia, telefono_emergencia):
        """Valida los datos del paciente"""
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
        
        if not fecha_nacimiento:
            errors.append("La fecha de nacimiento es requerida")
        else:
            try:
                fecha_obj = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
                if fecha_obj >= date.today():
                    errors.append("La fecha de nacimiento debe ser anterior a hoy")
                elif (date.today() - fecha_obj).days > 36500:  # ~100 años
                    errors.append("La fecha de nacimiento no puede ser mayor a 100 años")
            except ValueError:
                errors.append("Formato de fecha de nacimiento inválido")
        
        if not genero or genero not in ['M', 'F']:
            errors.append("El género es requerido y debe ser M o F")
        
        if not telefono or not telefono.strip():
            errors.append("El teléfono es requerido")
        elif not re.match(r'^[0-9+\-\s()]{10,15}$', telefono.strip()):
            errors.append("El formato del teléfono no es válido")
        
        if email and email.strip():
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email.strip()):
                errors.append("El formato del email no es válido")
        
        if not direccion or not direccion.strip():
            errors.append("La dirección es requerida")
        
        if not contacto_emergencia or not contacto_emergencia.strip():
            errors.append("El contacto de emergencia es requerido")
        
        if not telefono_emergencia or not telefono_emergencia.strip():
            errors.append("El teléfono de emergencia es requerido")
        elif not re.match(r'^[0-9+\-\s()]{10,15}$', telefono_emergencia.strip()):
            errors.append("El formato del teléfono de emergencia no es válido")
        
        return errors
    
    @staticmethod
    def calculate_age(fecha_nacimiento):
        """Calcula la edad basada en la fecha de nacimiento"""
        if isinstance(fecha_nacimiento, str):
            fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
        
        today = date.today()
        age = today.year - fecha_nacimiento.year
        
        if today.month < fecha_nacimiento.month or (today.month == fecha_nacimiento.month and today.day < fecha_nacimiento.day):
            age -= 1
        
        return age