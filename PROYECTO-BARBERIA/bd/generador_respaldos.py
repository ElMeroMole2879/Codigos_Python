import os
import subprocess
import time
from datetime import datetime
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
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
            
            # Mantenimiento de Servidor
            self._limpiar_respaldos_antiguos(dias_maximos=30)
            
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
                # El parámetro stdin empuja el texto del archivo hacia MySQL
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

    def _limpiar_respaldos_antiguos(self, dias_maximos=30):
        # Elimina los archivos .sql que tengan más de X días de antigüedad en la carpeta respaldo.
        tiempo_actual = time.time()
        tiempo_maximo = dias_maximos * 86400 # 86400 son los segundos que tiene un día
        
        # Iteramos por todos los archivos dentro de la carpeta de respaldos
        for nombre_archivo in os.listdir(self.carpeta_respaldo):
            ruta_archivo = os.path.join(self.carpeta_respaldo, nombre_archivo)
            
            # Validamos que sea un archivo y que termine en .sql
            if os.path.isfile(ruta_archivo) and nombre_archivo.endswith('.sql'):
                # Obtenemos la fecha en la que se modificó/creó el archivo
                tiempo_modificacion = os.path.getmtime(ruta_archivo)
                
                # Si la diferencia de tiempo es mayor al límite, lo borramos
                if (tiempo_actual - tiempo_modificacion) > tiempo_maximo:
                    try:
                        os.remove(ruta_archivo)
                        print(f"Mantenimiento: Respaldo antiguo eliminado -> {nombre_archivo}")
                    except Exception as e:
                        print(f"Mantenimiento: No se pudo eliminar el respaldo {nombre_archivo}. Error: {e}")