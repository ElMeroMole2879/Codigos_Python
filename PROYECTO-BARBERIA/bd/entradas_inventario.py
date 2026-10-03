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
                # Si algo falla (ej. el producto no existe), deshacemos AMBAS operaciones
                print(f"Error al registrar entrada de inventario: {e}")
                conexion.rollback() # rollback para deshacer cambios
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
                
                # Usamos INNER JOIN para saber qué producto compramos sin ver puros números
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
                # Glosario
                # e: Entradas_Inventario
                # p: Productos
                # INNER JOIN Productos p ON e.id_producto = p.id_producto
                # Dice que de la tabla Entradas_Inventario (e) se va a unir con la tabla Productos (p) donde el id_producto de Entradas coincida con el id_producto de Productos.
                
                cursor.execute(sql)
                return cursor.fetchall()
            except Exception as e:
                print(f"Error al obtener historial de entradas: {e}")
                return []
            finally:
                cursor.close()
                db.desconectar()
        return []