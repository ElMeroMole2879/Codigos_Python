from bd.conexion import ConexionDB
from datetime import datetime

class Venta:
    
    @staticmethod
    def registrar_venta(id_cliente, id_usuario, metodo_pago, total, lista_servicios, lista_productos):
        #Registra una venta completa (Ticket + Detalles + Descuento de Stock).
        # lista_servicios: lista de diccionarios [{'id_servicio': 1, 'id_empleado': 2, 'precio_cobrado': 250.00}]
        # lista_productos: lista de diccionarios [{'id_producto': 3, 'cantidad': 1, 'precio_cobrado': 150.00}]
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
                fecha_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Validar que haya stock suficiente ANTES de empezar la venta
                if lista_productos:
                    for prod in lista_productos:
                        cursor.execute("SELECT stock_total, nombre_producto FROM Productos WHERE id_producto = %s", (prod['id_producto'],))
                        resultado = cursor.fetchone()
                        
                        if not resultado:
                            print(f"Error: El producto con ID {prod['id_producto']} no existe.")
                            return None
                            
                        stock_actual = resultado[0] # El primer campo que pedimos
                        nombre_prod = resultado[1]  # El segundo campo
                        
                        if stock_actual < prod['cantidad']:
                            print(f"Alerta: No hay stock suficiente de '{nombre_prod}'. Tienes {stock_actual} y el cliente pide {prod['cantidad']}.")
                            return None # Cancelamos la venta antes de escribir nada en la BD
                
                # Insertar el ticket principal en Ventas
                sql_venta = """INSERT INTO Ventas (id_cliente, id_usuario, fecha_hora, total, metodo_pago) 
                               VALUES (%s, %s, %s, %s, %s)"""
                cursor.execute(sql_venta, (id_cliente, id_usuario, fecha_hora, total, metodo_pago))
                
                # Obtener el ID de la venta que se acaba de generar para usarlo en los detalles
                id_venta = cursor.lastrowid
                
                # Registrar los servicios realizados (para las comisiones)
                if lista_servicios:
                    sql_detalle_serv = """INSERT INTO Detalle_Venta_Servicios 
                                          (id_venta, id_servicio, id_empleado, precio_cobrado) 
                                          VALUES (%s, %s, %s, %s)"""
                    for serv in lista_servicios:
                        cursor.execute(sql_detalle_serv, (id_venta, serv['id_servicio'], serv['id_empleado'], serv['precio_cobrado']))
                
                # Registrar los productos vendidos y descontar el stock
                if lista_productos:
                    sql_detalle_prod = """INSERT INTO Detalle_Venta_Productos 
                                          (id_venta, id_producto, cantidad, precio_cobrado) 
                                          VALUES (%s, %s, %s, %s)"""
                    sql_descuento_stock = """UPDATE Productos 
                                             SET stock_total = stock_total - %s 
                                             WHERE id_producto = %s"""

                    for prod in lista_productos:
                        # Insertar en el detalle del ticket
                        cursor.execute(sql_detalle_prod, (id_venta, prod['id_producto'], prod['cantidad'], prod['precio_cobrado']))
                        # Restar del inventario
                        cursor.execute(sql_descuento_stock, (prod['cantidad'], prod['id_producto']))
                
                # Si todo salió bien, sellamos la transacción
                conexion.commit()
                print(f"Éxito: Venta #{id_venta} registrada correctamente por un total de ${total}.")
                return id_venta # Regresamos el número de ticket por si se quiere imprimir
                
            except Exception as e:
                # Si falla cualquier paso (ej. no hay stock suficiente), deshacemos absolutamente todo
                print(f"Error al registrar la venta (Transacción cancelada): {e}")
                conexion.rollback()
                return None
            finally:
                cursor.close()
                db.desconectar()
        return None

    @staticmethod
    def obtener_detalle_ticket(id_venta):
        #Devuelve toda la info de un ticket (cliente, empleado, servicios y productos) para imprimirlo.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                
                # Datos generales de la venta
                cursor.execute("""
                    SELECT v.id_venta, v.fecha_hora, v.total, v.metodo_pago, 
                           c.nombres AS cliente_nombres, c.primer_apellido AS cliente_apellido
                    FROM Ventas v
                    LEFT JOIN Clientes c ON v.id_cliente = c.id_cliente
                    WHERE v.id_venta = %s
                """, (id_venta,))
                # NOTA: Cambié a LEFT JOIN porque si borraron al cliente o fue "al público en general", aún así debe mostrar el ticket.
                venta = cursor.fetchone()
                
                if not venta:
                    return None

                # Servicios cobrados en este ticket
                cursor.execute("""
                    SELECT s.nombre_servicio, ds.precio_cobrado, e.nombres AS barbero
                    FROM Detalle_Venta_Servicios ds
                    INNER JOIN Servicios s ON ds.id_servicio = s.id_servicio
                    INNER JOIN Empleados e ON ds.id_empleado = e.id_empleado
                    WHERE ds.id_venta = %s
                """, (id_venta,))
                servicios = cursor.fetchall()

                # Productos vendidos en este ticket
                cursor.execute("""
                    SELECT p.nombre_producto, dp.cantidad, dp.precio_cobrado
                    FROM Detalle_Venta_Productos dp
                    INNER JOIN Productos p ON dp.id_producto = p.id_producto
                    WHERE dp.id_venta = %s
                """, (id_venta,))
                productos = cursor.fetchall()

                # Empaquetamos todo en un diccionario para la impresora o pantalla
                return {
                    "ticket": venta,
                    "servicios": servicios,
                    "productos": productos
                }

            except Exception as e:
                print(f"Error al obtener el detalle del ticket: {e}")
                return None
            finally:
                cursor.close()
                db.desconectar()
        return None

    @staticmethod
    def cancelar_venta_por_error(id_venta):
        
        # BORRADO FÍSICO CON REVERSIÓN DE INVENTARIO Y COMISIONES.
        # Elimina el ticket, le quita la comisión al barbero y devuelve los productos al estante.
        
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                
                # Validar que la venta exista antes de hacer nada
                cursor.execute("SELECT id_venta FROM Ventas WHERE id_venta = %s", (id_venta,))
                if not cursor.fetchone():
                    print(f"Error: No se encontró el ticket #{id_venta}.")
                    return False

                # Rescatar los productos que se vendieron para devolverlos al stock
                cursor.execute("SELECT id_producto, cantidad FROM Detalle_Venta_Productos WHERE id_venta = %s", (id_venta,))
                productos_vendidos = cursor.fetchall()
                
                # Devolver los productos al estante (Sumar stock_total)
                if productos_vendidos:
                    sql_devolver_stock = "UPDATE Productos SET stock_total = stock_total + %s WHERE id_producto = %s"
                    for prod in productos_vendidos:
                        cursor.execute(sql_devolver_stock, (prod['cantidad'], prod['id_producto']))

                # Eliminar el ticket principal (Tabla Ventas)
                # al borrar el ticket principal, MySQL borrará automáticamente las comisiones y 
                # los detalles de producto. Gracias a ON DELETE CASCADE
                cursor.execute("DELETE FROM Ventas WHERE id_venta = %s", (id_venta,))
                
                # Sellamos toda la operación en bloque
                conexion.commit()
                print(f"Éxito: Venta #{id_venta} cancelada. Inventario restaurado y comisiones eliminadas.")
                return True
                
            except Exception as e:
                # Si algo sale mal hacemos rollback para no descuadrar la caja
                print(f"Error crítico al intentar cancelar la venta: {e}")
                conexion.rollback()
                return False
            finally:
                cursor.close()
                db.desconectar()
        return False