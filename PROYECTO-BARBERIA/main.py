# Importamos el inicializador de la base de datos
from inicializar_bd import InicializadorBD
# Importamos tu clase de conexión para revisar el estado
from bd.conexion import ConexionDB

# Importamos la función main del archivo interfaz.py
from interfaz import main as iniciar_interfaz

if __name__ == "__main__":
    # Primero, le preguntamos a MySQL si la base de datos ya existe
    estado, detalle = ConexionDB.comprobar_estado_sistema()
    
    # SOLO si nos responde que NO existe, corremos el inicializador
    if estado == "NO_EXISTE_BD":
        db_init = InicializadorBD()
        db_init.configurar_base_datos()
        
    # Si el estado es "OK", Python se salta la instalación
    # Si el estado es error porque MySQL está apagado, tu archivo conexion.py 
    # ya cerró la app automáticamente con la ventana de "Cierre de Emergencia".
    
    # Inicia la interfaz gráfica de forma normal
    if estado == "OK" or estado == "NO_EXISTE_BD":
        iniciar_interfaz()