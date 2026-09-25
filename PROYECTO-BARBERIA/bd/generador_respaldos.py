import os
import subprocess
from datetime import datetime
from config import acceso_bd

# Clase para gestionar respaldos de bases de datos MySQL
class GestorRespaldos:
    def __init__(self):
        # Obtenemos la ruta absoluta del directorio actual del archivo generador_respaldos.py
        self.carpeta_soporte = os.path.dirname(__file__)

        # Sube un nivel para llegar a la raíz (PROYECTO-BARBERIA)
        self.carpeta_principal = os.path.dirname(self.carpeta_soporte)
        
        # Crea la ruta hacia la carpeta 'respaldo' en la raíz del proyecto
        self.carpeta_respaldo = os.path.join(self.carpeta_principal, "respaldo")

    # Función para crear un respaldo de la base de datos
    def crear_respaldo(self):
        # Verificamos si la carpeta "respaldo" existe, si no la creamos
        if not os.path.exists(self.carpeta_respaldo): 
            os.makedirs(self.carpeta_respaldo) 
            print(f"Carpeta creada en: {self.carpeta_respaldo}")

        # Generamos un nombre único con la fecha y hora actual
        fecha_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # FIX: Usamos acceso_bd['database'] en lugar de self.db_name
        nombre_archivo = f"backup_{acceso_bd['database']}_{fecha_hora}.sql"
        ruta_completa = os.path.join(self.carpeta_respaldo, nombre_archivo)

        # Comando para generar el respaldo usando mysqldump
        comando = [
            "mysqldump",
            "-u", acceso_bd["user"],
            f"-p{acceso_bd['password']}",
            acceso_bd["database"]
        ]

        try:
            print("Generando respaldo de la base de datos...")
            # Usamos stdout para redirigir la salida del comando hacia el archivo .sql
            with open(ruta_completa, "w", encoding="utf-8") as archivo_salida:
                subprocess.run(comando, stdout=archivo_salida, check=True)
                
            print(f"¡Respaldo creado con éxito!\nRuta: {ruta_completa}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error al generar el respaldo: {e}")
            return False
        except Exception as e:
            print(f"Error inesperado al crear respaldo: {e}")
            return False

    def restaurar_respaldo(self, ruta_archivo):
        # Comando para restaurar la base de datos (mysql)
        comando = [
            "mysql",
            "-u", acceso_bd["user"],
            f"-p{acceso_bd['password']}",
            acceso_bd["database"]
        ]

        # Abrimos el archivo .sql y lo inyectamos a la base de datos
        try:
            with open(ruta_archivo, "r", encoding="utf-8") as archivo_entrada:
                # El parámetro stdin "empuja" el texto del archivo hacia MySQL
                subprocess.run(comando, stdin=archivo_entrada, check=True)
            print(f"Base de datos restaurada con éxito desde: {ruta_archivo}")
            return True
            
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo de respaldo en {ruta_archivo}")
            return False
        except subprocess.CalledProcessError as e:
            print(f"Error crítico al restaurar la base de datos: {e}")
            return False
        except Exception as e:
            print(f"Error inesperado: {e}")
            return False