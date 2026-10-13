from bd.conexion import ConexionDB

class EntradaInventario:
    
    @staticmethod
    def registrar_entrada(id_producto, fecha_llegada, cantidad, costo_unitario, fecha_caducidad=None):
        #Registra la compra de mercancía y SUMA la cantidad al stock del producto automáticamente.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
                
                # Guardar el historial de la entrada
                sql_entrada = """INSERT INTO Entradas_Inventario 
                                 (id_producto, fecha_llegada, cantidad, costo_unitario, fecha_caducidad) 
                                 VALUES (%s, %s, %s, %s, %s)"""
                valores_entrada = (id_producto, fecha_llegada, cantidad, costo_unitario, fecha_caducidad)
                cursor.execute(sql_entrada, valores_entrada)
                
                # Actualizar (sumar) el stock en la tabla Productos
                sql_stock = """UPDATE Productos 
                               SET stock_total = stock_total + %s 
                               WHERE id_producto = %s"""
                valores_stock = (cantidad, id_producto)
                cursor.execute(sql_stock, valores_stock)
                
                # Si ambos pasos salieron bien, sellamos la transacción
                conexion.commit() 
                print(f"Éxito: Entrada registrada. Se sumaron {cantidad} unidades al producto ID {id_producto}.")
                return True
                
            except Exception as e:
                # Si algo falla, deshacemos AMBAS operaciones
                print(f"Error al registrar entrada de inventario: {e}")
                conexion.rollback() 
                return False
            finally:
                cursor.close()
                db.desconectar()
        return False

    @staticmethod
    def obtener_todas_las_entradas():
        #Trae el historial de entradas cruzando con la tabla Productos para ver su nombre real.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True) 
                sql = """
                SELECT 
                    e.id_entrada,
                    p.nombre_producto,
                    p.marca,
                    e.fecha_llegada,
                    e.cantidad,
                    e.costo_unitario,
                    e.fecha_caducidad
                FROM Entradas_Inventario e
                INNER JOIN Productos p ON e.id_producto = p.id_producto
                ORDER BY e.fecha_llegada DESC
                """
                cursor.execute(sql)
                return cursor.fetchall()
            except Exception as e:
                print(f"Error al obtener historial de entradas: {e}")
                return []
            finally:
                cursor.close()
                db.desconectar()
        return []
    
    @staticmethod
    def eliminar_entrada_por_error(id_entrada):
        
        # BORRADO FÍSICO (DELETE) con reversión de inventario.
        # Borra el registro de compra y le RESTA esa cantidad al stock principal.
        
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                
                # Consultar de cuánto fue la entrada original y a qué producto pertenece
                cursor.execute("SELECT id_producto, cantidad FROM Entradas_Inventario WHERE id_entrada = %s", (id_entrada,))
                entrada = cursor.fetchone()
                
                if not entrada:
                    print("Error: No se encontró el registro de entrada.")
                    return False
                    
                id_prod = entrada['id_producto']
                cantidad_a_restar = entrada['cantidad']
                
                # Consultar el stock actual del producto para evitar números negativos
                cursor.execute("SELECT stock_total FROM Productos WHERE id_producto = %s", (id_prod,))
                stock_actual = cursor.fetchone()['stock_total']
                
                if (stock_actual - cantidad_a_restar) < 0:
                    print(f"Alerta: No se puede borrar esta entrada. El stock quedaría en negativo ({- (stock_actual - cantidad_a_restar)}).")
                    print("Probablemente parte de esta mercancía ya fue vendida en la caja.")
                    return False
                
                # Restar el stock en la tabla Productos
                sql_restar_stock = "UPDATE Productos SET stock_total = stock_total - %s WHERE id_producto = %s"
                cursor.execute(sql_restar_stock, (cantidad_a_restar, id_prod))
                
                # Eliminar el registro histórico de la entrada
                sql_borrar_entrada = "DELETE FROM Entradas_Inventario WHERE id_entrada = %s"
                cursor.execute(sql_borrar_entrada, (id_entrada,))
                
                # Sellamos las dos operaciones
                conexion.commit()
                print(f"Éxito: Entrada {id_entrada} eliminada. Se descontaron {cantidad_a_restar} unidades del inventario.")
                return True
                
            except Exception as e:
                print(f"Error al intentar eliminar la entrada: {e}")
                conexion.rollback()
                return False
            finally:
                cursor.close()
                db.desconectar()
        return False