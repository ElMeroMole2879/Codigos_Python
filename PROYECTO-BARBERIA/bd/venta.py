from bd.conexion import ConexionDB
from datetime import datetime

class Venta:
    
    @staticmethod
    def registrar_venta(id_cliente, id_usuario, metodo_pago, total, lista_servicios, lista_productos):
        # Registra una venta completa (Ticket + Detalles + Descuento de Stock).
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
                
                # Si la venta tiene un cliente asignado, marcar su cita de hoy como Completada
                if id_cliente is not None:
                    cursor.execute(
                        "UPDATE citas SET estado = 'Completada' WHERE id_cliente = %s AND fecha_cita = CURDATE() AND estado = 'Pendiente'", 
                        (id_cliente,)
                    )
        
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

    @classmethod
    def obtener_detalle_ticket(cls, id_venta):
        db = ConexionDB()
        conexion = db.conectar()
        if not conexion: return None
        try:
            cursor = conexion.cursor(dictionary=True)
            
            sql_ticket = """
                SELECT v.*, 
                       c.nombres AS cliente_nombres, c.primer_apellido AS cliente_apellido,
                       u.nombres AS cajero_nombres, u.primer_apellido AS cajero_apellido
                FROM Ventas v
                LEFT JOIN Clientes c ON v.id_cliente = c.id_cliente
                LEFT JOIN Usuarios u ON v.id_usuario = u.id_usuario
                WHERE v.id_venta = %s
            """
            cursor.execute(sql_ticket, (id_venta,))
            ticket = cursor.fetchone()
            if not ticket: return None
            
            # Usando el nombre exacto de la tabla 10 de tu inicializar_bd.py
            sql_servicios = """
                SELECT vs.precio_cobrado, s.nombre_servicio, 
                       CONCAT(e.nombres, ' ', IFNULL(e.primer_apellido, '')) as barbero
                FROM Detalle_Venta_Servicios vs
                JOIN Servicios s ON vs.id_servicio = s.id_servicio
                JOIN Empleados e ON vs.id_empleado = e.id_empleado
                WHERE vs.id_venta = %s
            """
            cursor.execute(sql_servicios, (id_venta,))
            servicios = cursor.fetchall()
            
            # Usando el nombre exacto de la tabla 11 de tu inicializar_bd.py
            sql_productos = """
                SELECT vp.cantidad, vp.precio_cobrado, p.nombre_producto
                FROM Detalle_Venta_Productos vp
                JOIN Productos p ON vp.id_producto = p.id_producto
                WHERE vp.id_venta = %s
            """
            cursor.execute(sql_productos, (id_venta,))
            productos = cursor.fetchall()
            
            return {
                "ticket": ticket,
                "servicios": servicios,
                "productos": productos
            }
        except Exception as e:
            raise Exception(f"Falla en la base de datos al buscar el ticket:\n{e}")
        finally:
            if 'cursor' in locals(): cursor.close()
            db.desconectar()

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

    @classmethod
    def buscar_ventas_por_termino(cls, termino):
        db = ConexionDB()
        conexion = db.conectar()
        if not conexion: return []
        try:
            cursor = conexion.cursor(dictionary=True)
            sql = """
                SELECT v.id_venta, v.fecha_hora, v.metodo_pago, v.total,
                       c.nombres, c.primer_apellido, c.segundo_apellido
                FROM Ventas v
                LEFT JOIN Clientes c ON v.id_cliente = c.id_cliente
                WHERE v.id_venta LIKE %s 
                   OR v.fecha_hora LIKE %s 
                   OR c.nombres LIKE %s 
                   OR c.primer_apellido LIKE %s 
                   OR c.segundo_apellido LIKE %s
                ORDER BY v.id_venta DESC
                LIMIT 50
            """
            like_term = f"%{termino}%"
            cursor.execute(sql, (like_term, like_term, like_term, like_term, like_term))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al buscar ventas: {e}")
            return []
        finally:
            if 'cursor' in locals(): cursor.close()
            db.desconectar()