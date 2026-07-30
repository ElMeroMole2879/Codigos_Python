import subprocess
import datetime
import getpass

# DATOS DE CONEXION
usuario = "root"
base_datos = "world"
archivo_salida = f"C:/Copias/backup_{base_datos}_{datetime.datetime.now():%Y%m%d_%H%M%S}.sql"

# PEDIR CONTRASEÑA

contrasena = getpass.getpass("Introduce la contraseña de MySQL: ")

# COMANDO COMO LISTA PARA EVITAR SHELL = TRUE

comando =[
    "mysqldump",
    f"--user={usuario}",
    f"--password={contrasena}",
    "..databases",
    base_datos
]

try:
    with open(archivo_salida, "w", encoding="utf-8") as salida:
        #COMANDO EN FORMA SEGURA
        resultado = subprocess.run(comando, stdout=salida, stderr=subprocess.PIPE, text=True,
        check=True)
        print(f"Copia de seguridad completada: {archivo_salida}")
    
except subprocess.CalledProcessError as e:
    print("Error al hacer la copia de seguridad.")
    print("Mensaje de error:", e.stderr)

except FileNotFoundError:
    print("Error: No se encontro 'mysqldump'. Asegurate de que esta en el PATH del sistema")