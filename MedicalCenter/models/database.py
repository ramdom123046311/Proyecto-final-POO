import mysql.connector
from mysql.connector import Error
import hashlib

class Database:
    def __init__(self):
        self.host = 'localhost'
        self.database = 'medicalcenter'
        self.user = 'root'
        self.password = 'admin'
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Establece conexión con la base de datos"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            if self.connection.is_connected():
                self.cursor = self.connection.cursor()
                return True
        except Error as e:
            print(f"Error al conectar a MySQL: {e}")
            return False
        return False
    
    def disconnect(self):
        """Cierra la conexión con la base de datos"""
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
    
    def execute_query(self, query, params=None):
        """Ejecuta una consulta SELECT y retorna los resultados"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            return self.cursor.fetchall()
        except Error as e:
            print(f"Error ejecutando consulta: {e}")
            return None
    
    def execute_update(self, query, params=None):
        """Ejecuta una consulta INSERT, UPDATE o DELETE"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            self.connection.commit()
            return self.cursor.rowcount
        except Error as e:
            print(f"Error ejecutando actualización: {e}")
            self.connection.rollback()
            return 0
    
    def get_last_insert_id(self):
        """Retorna el último ID insertado"""
        return self.cursor.lastrowid

# Función utilitaria para hash de contraseñas
def hash_password(password):
    """Genera hash SHA-256 de la contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()

# Instancia global de la base de datos
db = Database()