from bd.usuario import Usuario
from bd.cliente import Cliente
from bd.citas import Cita

def simular_frontend():
    print("=========================================")
    print("  SIMULACIÓN DE BACKEND PARA EL EQUIPO   ")
    print("=========================================\n")

    print("--- PASO 1: PRUEBA DE INICIO DE SESIÓN (LOGIN) ---")
    print("-> El frontend envía: Usuario 'admin' / Password '12345'")
    usuario_valido = Usuario.validar_login('admin', '12345')
    
    if usuario_valido == "INACTIVO":
        print("BACKEND RESPONDE: El usuario existe pero está dado de baja.")
    elif usuario_valido:
        print(f"BACKEND RESPONDE: Login exitoso. Rol = {usuario_valido['rol']}, ID = {usuario_valido['id_usuario']}")
    else:
        print("BACKEND RESPONDE: Error de credenciales.")

    print("\n--- PASO 2: PRUEBA DE REGISTRO DE CLIENTE Y CITA ---")
    print("-> El frontend envía datos para un nuevo cliente: 'Juan Perez Gomez'")
    
    # Probamos el registro del cliente
    exito_cliente = Cliente.registrar_cliente('Juan', 'Perez', 'Gomez', '8181234567', 'Low Fade')
    if exito_cliente:
        print("BACKEND RESPONDE: Cliente guardado correctamente en la BD.")
    else:
        print("BACKEND RESPONDE: Fallo al guardar cliente.")

    print("\n-> El frontend solicita agendar una cita (Asumiendo Cliente 1, Barbero 1, Servicio 1)...")
    # Probamos agendar la cita para el 15 de octubre
    exito_cita = Cita.agendar_cita(1, 1, 1, '2026-10-15', '15:00:00')
    if exito_cita:
        print("BACKEND RESPONDE: Cita agendada correctamente con estado 'Pendiente'.")
    else:
        print("BACKEND RESPONDE: Error al agendar cita. (Aviso: La BD protegió la integridad referencial).")

if __name__ == "__main__":
    simular_frontend()