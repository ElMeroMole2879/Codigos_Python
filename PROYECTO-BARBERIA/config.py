import sys
import os

# La ruta del proyecto al sistema para que todos los módulos se puedan encontrar entre sí sin errores.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configuración de la base de datos
acceso_bd = {
    "host": "localhost",
    "user": "admin_barberia",
    "password": "Barberia2026*",
    "database": "barberia_bd",
    "port": 3306
}