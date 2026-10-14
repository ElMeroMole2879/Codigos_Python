import sys
import os

# Aseguramos que Python encuentre la carpeta bd/
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from bd.usuario import Usuario
from bd.producto import Producto
from bd.servicios import Servicio
from bd.cliente import Cliente
from bd.empleados import Empleado
from bd.venta import Venta
from bd.reportes import Reporte

def simular_sistema():
    print("==================================================")
    print("   PRUEBA BACKEND  ")
    print("==================================================")

    # PRUEBA DE LOGIN
    print("\n[1] Probando Inicio de Sesión...")
    # Usamos el usuario admin por defecto creado en la inicialización
    usuario_logueado = Usuario.validar_login("admin", "12345")
    
    if usuario_logueado and usuario_logueado != "INACTIVO":
        print(f"-> Login exitoso Bienvenido al sistema, {usuario_logueado['nombres']} ({usuario_logueado['rol']}).")
    else:
        print(" Error: No se pudo iniciar sesión. Verifica que hayas ejecutado 'inicializar_bd.py'.")
        return

    # CONSULTAR CATÁLOGOS (Productos y Servicios)
    print("\n [2] Consultando Catálogos Disponibles...")
    productos = Producto.obtener_todos_los_productos()
    servicios = Servicio.obtener_todos_los_servicios()
    
    print(f"Productos en inventario: {len(productos)}")
    for p in productos:
        print(f" ID: {p['id_producto']} | {p['nombre_producto']} ({p['marca']}) - Stock: {p['stock_total']} - Precio: ${p['precio_venta_actual']}")

    print(f" Servicios disponibles: {len(servicios)}")
    for s in servicios:
        print(f" ID: {s['id_servicio']} | {s['nombre_servicio']} - ${s['precio_actual']} ({s['duracion_minutos']} mins)")

    # SIMULAR UNA VENTA COMPLETA (Punto de Venta)
    print("\n[3] Simulando una Venta en Caja...")
    # Para esta prueba, asumimos que ya existe un cliente y un empleado en la base de datos.
    id_cliente_prueba = 1 
    id_empleado_prueba = 1
    id_usuario_prueba = usuario_logueado['id_usuario']

    # Simularemos que el cliente compra 1 Cera (ID 1) y se hace un Corte (ID 1)
    # Buscamos el precio real del primer producto y primer servicio si existen
    if productos and servicios:
        prod_sel = productos[0]
        serv_sel = servicios[0]

        lista_servicios = [
            {"id_servicio": serv_sel['id_servicio'], "id_empleado": id_empleado_prueba, "precio_cobrado": float(serv_sel['precio_actual'])}
        ]
        
        lista_productos = [
            {"id_producto": prod_sel['id_producto'], "cantidad": 1, "precio_cobrado": float(prod_sel['precio_venta_actual'])}
        ]

        total_venta = float(serv_sel['precio_actual']) + float(prod_sel['precio_venta_actual'])
        metodo_pago = "Efectivo"

        print(f" Procesando ticket por un total de ${total_venta}...")
        id_venta_generada = Venta.registrar_venta(
            id_cliente=id_cliente_prueba,
            id_usuario=id_usuario_prueba,
            metodo_pago=metodo_pago,
            total=total_venta,
            lista_servicios=lista_servicios,
            lista_productos=lista_productos
        )

        if id_venta_generada:
            print(f" Venta registrada con éxito bajo el Ticket #{id_venta_generada}")

            # VERIFICAR CORTE DE CAJA DIARIO
            print("\n[4] Consultando Corte de Caja del Día")
            corte = Reporte.obtener_corte_caja_diario()
            print(f" Fecha del Corte: {corte['fecha_corte']}")
            print(f" Gran Total Vendido: ${corte['gran_total_del_dia']}")
            print(f" Desglose por método de pago:")
            for desglose in corte['desglose_por_metodo']:
                print(f" * {desglose['metodo_pago']}: ${desglose['total_recaudado']} ({desglose['numero_tickets']} tickets)")
        else:
            print(" La venta no pudo completarse (probablemente por falta de stock).")
    else:
        print(" Advertencia: No hay suficientes productos o servicios en la BD para simular la venta. Agrega algunos desde la BD o inicializala.")

    print("\n==================================================")
    print("      PRUEBA FINALIZADA CORRECTAMENTE            ")
    print("==================================================")

if __name__ == "__main__":
    simular_sistema()