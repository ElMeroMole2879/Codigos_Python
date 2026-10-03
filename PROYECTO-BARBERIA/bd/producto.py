from bd.conexion import ConexionDB

class Producto:
    
    @staticmethod
    def registrar_producto(nombre_producto, marca, precio_venta_actual, stock_total):
        #Registra un nuevo producto físico en el inventario.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = """INSERT INTO PRODUCTOS (nombre_producto, marca, precio_venta_actual, stock_total) 
                         VALUES (%s, %s, %s, %s)"""
                valores = (nombre_producto, marca, precio_venta_actual, stock_total)
                
                cursor.execute(sql, valores)
                conexion.commit()
                print(f"Éxito: Producto '{nombre_producto}' de marca '{marca}' registrado.")
                return True
                
            except Exception as e:
                print(f"Error al registrar producto: {e}")
                conexion.rollback()
                return False
            finally:
                cursor.close()
                db.desconectar()
        return False

    @staticmethod
    def obtener_todos_los_productos():
        #Trae el catálogo completo de productos en inventario.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True) # dictionary=True hace que los resultados regresen como un diccionario (clave-valor)
                cursor.execute("SELECT * FROM PRODUCTOS ORDER BY nombre_producto ASC")
                return cursor.fetchall()
            except Exception as e:
                print(f"Error al obtener productos: {e}")
                return []
            finally:
                cursor.close()
                db.desconectar()
        return []

    @staticmethod
    def actualizar_stock(id_producto, cantidad_a_sumar):
        #Suma o resta stock al inventario (útil para nuevas compras o ajustes de inventario).
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
                # Usamos una consulta que actualiza sumando al stock actual
                sql = "UPDATE PRODUCTOS SET stock_total = stock_total + %s WHERE id_producto = %s"
                cursor.execute(sql, (cantidad_a_sumar, id_producto))
                conexion.commit()
                print(f"Éxito: Stock del producto {id_producto} actualizado.")
                return True
                
            except Exception as e:
                print(f"Error al actualizar el stock: {e}")
                conexion.rollback()
                return False
            finally:
                cursor.close()
                db.desconectar()
        return False

    @staticmethod
    def actualizar_precio_producto(id_producto, nuevo_precio):
        #Actualiza el precio de venta de un producto.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = "UPDATE PRODUCTOS SET precio_venta_actual = %s WHERE id_producto = %s"
                cursor.execute(sql, (nuevo_precio, id_producto))
                conexion.commit()
                print(f"Éxito: Precio del producto {id_producto} actualizado a ${nuevo_precio}.")
                return True
                
            except Exception as e:
                print(f"Error al actualizar el precio: {e}")
                conexion.rollback()
                return False
            finally:
                cursor.close()
                db.desconectar()
        return False