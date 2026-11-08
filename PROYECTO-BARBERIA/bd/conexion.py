import mysql.connector
from mysql.connector import Error
from tkinter import messagebox  # <-- Importación para la ventana de error
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import acceso_bd

class ConexionDB:
    def __init__(self):
        # Guardamos las credenciales de la base de datos en un atributo de la clase
        self.credenciales = acceso_bd
        self.conexion = None

    def conectar(self, mostrar_alerta=True):
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
            # Imprimimos en consola el error real para el programador
            print(f"Alerta Crítica: No hay conexión a la BD. Detalle: {e}")
            
            if mostrar_alerta:
                # Modificamos el mensaje para avisar que el programa se va a cerrar
                mensaje_profesional = (
                    "Error Crítico de Conexión: Se ha perdido la comunicación con el servidor de base de datos MySQL.\n\n"
                    "Por seguridad y para proteger la integridad de los datos, el sistema se cerrará automáticamente.\n\n"
                    "Por favor, verifique que el servidor esté encendido o contacte a soporte técnico antes de volver a abrir la aplicación."
                )
                messagebox.showerror("Cierre de Emergencia", mensaje_profesional)
                
                # Ejecutamos un cierre forzoso e inmediato de la aplicación (Kill Process)
                # Esto destruye la ventana de Tkinter y saca al usuario de la app.
                import os
                os._exit(1)
                
            else:
                # Si estamos comprobando el sistema al inicio, lanzamos el error
                raise e

    def desconectar(self):
        if self.conexion and self.conexion.is_connected():
            self.conexion.close()

    @classmethod
    def comprobar_estado_sistema(cls):
        import mysql.connector
        try:
            db = cls() #cls crea una instancia de la clase ConexionDB
            # Pasamos mostrar_alerta=False para que el error suba a este try-except
            # y no salte la ventana emergente antes de que cargue el programa.
            conexion = db.conectar(mostrar_alerta=False)
            if conexion:
                conexion.close()
                return "OK", None
            return "ERROR_DESCONOCIDO", "No se pudo establecer la conexión."
        except mysql.connector.Error as e:
            if e.errno == 1049:
                return "NO_EXISTE_BD", e
            return "ERROR_CONEXION", e