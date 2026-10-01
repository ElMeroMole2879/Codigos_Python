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