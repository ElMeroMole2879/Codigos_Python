from bd.conexion import ConexionDB
from datetime import datetime

class Venta:
    
    @staticmethod
    def registrar_venta(id_cliente, id_usuario, metodo_pago, total, lista_servicios, lista_productos):
        #Registra una venta completa (Ticket + Detalles + Descuento de Stock).
        # - lista_servicios: lista de diccionarios [{'id_servicio': 1, 'id_empleado': 2, 'precio_cobrado': 250.00}]
        # - lista_productos: lista de diccionarios [{'id_producto': 3, 'cantidad': 1, 'precio_cobrado': 150.00}]
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
                # sql_venta es la consulta SQL que inserta un nuevo registro en la tabla Ventas.
                
                # Obtener el ID de la venta que se acaba de generar para usarlo en los detalles
                id_venta = cursor.lastrowid
                # lastrowid nos da el último ID insertado en la tabla Ventas, que es el ticket que acabamos de crear.
                
                # PASO 2: Registrar los servicios realizados (para las comisiones)
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

                    # %s nos permite pasar los valores de manera segura, evitando inyecciones SQL.
                    
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