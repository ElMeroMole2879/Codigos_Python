# Importamos el inicializador de la base de datos
from inicializar_bd import InicializadorBD

# Importamos la función main del archivo interfaz.py
from interfaz import main as iniciar_interfaz

if __name__ == "__main__":
    # Verificamos y construimos la base de datos
    # Si no existe, la crea. Si ya existe, la respeta y continúa.
    db_init = InicializadorBD()
    db_init.configurar_base_datos()
    
    # Inicia la interfaz gráfica
    iniciar_interfaz()