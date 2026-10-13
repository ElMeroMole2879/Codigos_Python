import mysql.connector
from mysql.connector import Error
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import acceso_bd

class ConexionDB:
    def __init__(self):
        # Guardamos las credenciales de la base de datos en un atributo de la clase
        self.credenciales = acceso_bd
        self.conexion = None

    def conectar(self):
        # Intentamos establecer la conexión a la base de datos usando las credenciales
        try:
            self.conexion = mysql.connector.connect(
                host=self.credenciales["host"],
                user=self.credenciales["user"],
                password=self.credenciales["password"],
                database=self.credenciales["database"],
                port=self.credenciales["port"],
                connection_timeout=5 # Tiempo de espera de 5 segundos para la conexión
                )
            
            if self.conexion.is_connected():
                return self.conexion
                
        except Error as e:
            # Si se le olvida prender el servidor
            print(f"Alerta Crítica: No hay conexión a la BD. Revisa tu conexión o enciende el servidor MySQL. Detalle: {e}")
            return None

    def desconectar(self):
        if self.conexion and self.conexion.is_connected():
            self.conexion.close()