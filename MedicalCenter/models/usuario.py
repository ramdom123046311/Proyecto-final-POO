from .database import db, hash_password

class Usuario:
    def __init__(self):
        pass
    
    @staticmethod
    def authenticate(rfc, password):
        """Autentica un usuario con RFC y contraseña"""
        hashed_password = hash_password(password)
        query = "SELECT * FROM usuarios WHERE rfc = %s AND contrasena = %s"
        result = db.execute_query(query, (rfc, hashed_password))
        
        if result:
            user_data = result[0]
            return {
                'id': user_data[0],
                'rfc': user_data[1],
                'nombre': 'Usuario',  # La tabla no tiene nombre/apellidos
                'apellido_paterno': '',
                'apellido_materno': '',
                'privilegio': user_data[3]
            }
        return None
    
    @staticmethod
    def get_by_id(user_id):
        """Obtiene un usuario por su ID"""
        query = "SELECT * FROM usuarios WHERE id_usuario = %s"
        result = db.execute_query(query, (user_id,))
        
        if result:
            user_data = result[0]
            return {
                'id': user_data[0],
                'rfc': user_data[1],
                'nombre': 'Usuario',
                'apellido_paterno': '',
                'apellido_materno': '',
                'privilegio': user_data[3]
            }
        return None
    
    @staticmethod
    def get_all():
        """Obtiene todos los usuarios"""
        query = "SELECT * FROM usuarios"
        result = db.execute_query(query)
        
        users = []
        if result:
            for user_data in result:
                users.append({
                    'id': user_data[0],
                    'rfc': user_data[1],
                    'nombre': 'Usuario',
                    'apellido_paterno': '',
                    'apellido_materno': '',
                    'privilegio': user_data[3]
                })
        return users
    
    @staticmethod
    def create(rfc, password, privilegio):
        """Crea un nuevo usuario"""
        hashed_password = hash_password(password)
        query = """INSERT INTO usuarios (rfc, contrasena, privilegio, estatus) 
                   VALUES (%s, %s, %s, %s)"""
        
        result = db.execute_update(query, (rfc, hashed_password, privilegio, 1))
        
        if result > 0:
            return db.get_last_insert_id()
        return None
    
    @staticmethod
    def update(user_id, rfc, privilegio, password=None):
        """Actualiza un usuario existente"""
        if password:
            hashed_password = hash_password(password)
            query = """UPDATE usuarios SET rfc = %s, contrasena = %s, privilegio = %s WHERE id_usuario = %s"""
            params = (rfc, hashed_password, privilegio, user_id)
        else:
            query = """UPDATE usuarios SET rfc = %s, privilegio = %s WHERE id_usuario = %s"""
            params = (rfc, privilegio, user_id)
        
        return db.execute_update(query, params) > 0
    
    @staticmethod
    def delete(user_id):
        """Elimina un usuario"""
        query = "DELETE FROM usuarios WHERE id_usuario = %s"
        return db.execute_update(query, (user_id,)) > 0
    
    @staticmethod
    def exists_rfc(rfc, exclude_id=None):
        """Verifica si un RFC ya existe"""
        if exclude_id:
            query = "SELECT COUNT(*) FROM usuarios WHERE rfc = %s AND id_usuario != %s"
            result = db.execute_query(query, (rfc, exclude_id))
        else:
            query = "SELECT COUNT(*) FROM usuarios WHERE rfc = %s"
            result = db.execute_query(query, (rfc,))
        
        return result and result[0][0] > 0