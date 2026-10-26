from bd.conexion import ConexionDB

class Producto:
    
    @staticmethod
    def registrar_producto(nombre_producto, marca, precio_venta_actual, stock_total):
        # Validación de precios y stock
        if precio_venta_actual <= 0:
            raise ValueError("El precio del producto debe ser mayor a $0.")
        if stock_total < 0:
            raise ValueError("El stock inicial no puede ser menor a 0.")

        # Registra un nuevo producto físico en el inventario.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = """INSERT INTO Productos (nombre_producto, marca, precio_venta_actual, stock_total) 
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
        # Trae el catálogo completo de productos en inventario.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                cursor.execute("SELECT * FROM Productos ORDER BY nombre_producto ASC")
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
        # Suma o resta stock al inventario (útil para nuevas compras o ajustes de inventario).
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = "UPDATE Productos SET stock_total = stock_total + %s WHERE id_producto = %s"
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
        # Validación para no permitir precios en cero o negativos
        if nuevo_precio <= 0:
            raise ValueError("El nuevo precio debe ser mayor a $0.")

        # Actualiza el precio de venta de un producto.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = "UPDATE Productos SET precio_venta_actual = %s WHERE id_producto = %s"
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

    @staticmethod
    def editar_producto(id_producto, nombre_producto, marca):
        # Edita los datos de texto (nombre y marca) si hubo un error ortográfico.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = "UPDATE Productos SET nombre_producto = %s, marca = %s WHERE id_producto = %s"
                cursor.execute(sql, (nombre_producto, marca, id_producto))
                conexion.commit()
                print(f"Éxito: Datos del producto {id_producto} actualizados.")
                return True
                
            except Exception as e:
                print(f"Error al editar producto: {e}")
                conexion.rollback()
                return False
            finally:
                cursor.close()
                db.desconectar()
        return False

    @staticmethod
    def eliminar_producto_por_error(id_producto):
        
        # BORRADO FÍSICO (DELETE) con validación de seguridad.
        # Solo permite borrar si NUNCA ha sido comprado a un proveedor ni vendido a un cliente.
        
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
                
                # Validar Entradas de Inventario
                cursor.execute("SELECT COUNT(*) FROM Entradas_Inventario WHERE id_producto = %s", (id_producto,))
                tiene_entradas = cursor.fetchone()[0]
                
                # Validar si ya se vendió alguna vez
                cursor.execute("SELECT COUNT(*) FROM Detalle_Venta_Productos WHERE id_producto = %s", (id_producto,))
                tiene_ventas = cursor.fetchone()[0]
                
                if tiene_entradas > 0 or tiene_ventas > 0:
                    print(f"Alerta: No se puede borrar físicamente el producto {id_producto} porque tiene historial de compras o ventas.")
                    print("Por favor, edita su nombre o simplemente deja su stock en 0 para que se marque como 'Agotado'.")
                    return False
                
                # Si está limpio, procedemos con el borrado físico
                sql = "DELETE FROM Productos WHERE id_producto = %s"
                cursor.execute(sql, (id_producto,))
                
                if cursor.rowcount > 0:
                    conexion.commit()
                    print(f"Éxito: Producto {id_producto} eliminado físicamente por error de captura.")
                    return True
                else:
                    print("Error: No se encontró el producto.")
                    return False
                
            except Exception as e:
                print(f"Error al intentar eliminar el producto: {e}")
                conexion.rollback()
                return False
            finally:
                cursor.close()
                db.desconectar()
        return False