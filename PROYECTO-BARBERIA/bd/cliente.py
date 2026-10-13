from bd.conexion import ConexionDB

class Cliente:
    
    @staticmethod
    def registrar_cliente(nombres, primer_apellido, segundo_apellido, telefono, corte_preferido=None):
        # Guarda un nuevo cliente en la base de datos.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = """INSERT INTO Clientes (nombres, primer_apellido, segundo_apellido, telefono, corte_preferido) 
                         VALUES (%s, %s, %s, %s, %s)"""
                valores = (nombres, primer_apellido, segundo_apellido, telefono, corte_preferido)
                
                cursor.execute(sql, valores)
                conexion.commit()
                print(f"Éxito: Cliente '{nombres} {primer_apellido}' registrado correctamente.")
                return True
                
            except Exception as e:
                print(f"Error al registrar cliente: {e}")
                conexion.rollback()
                return False
            finally:
                cursor.close()
                db.desconectar()
        return False

    @staticmethod
    def obtener_todos_los_clientes():
        # Trae la lista de clientes activos ordenados por nombre.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True) 
                cursor.execute("SELECT * FROM Clientes WHERE activo = True ORDER BY nombres ASC")
                return cursor.fetchall()
            except Exception as e:
                print(f"Error al obtener clientes: {e}")
                return []
            finally:
                cursor.close()
                db.desconectar()
        return []

    @staticmethod
    def dar_de_baja(id_cliente):
        # Realiza una baja lógica del cliente (activo = False) en lugar de borrarlo.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = "UPDATE Clientes SET activo = False WHERE id_cliente = %s"
                cursor.execute(sql, (id_cliente,))
                conexion.commit()
                
                print(f"Éxito: Cliente {id_cliente} dado de baja (oculto) del sistema.")
                return True
                
            except Exception as e:
                print(f"Error al dar de baja al cliente: {e}")
                conexion.rollback()
                return False
            finally:
                cursor.close()
                db.desconectar()
        return False

    @staticmethod
    def reactivar_cliente(id_cliente):
        # Vuelve a activar a un cliente que había sido dado de baja.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = "UPDATE Clientes SET activo = True WHERE id_cliente = %s"
                cursor.execute(sql, (id_cliente,))
                conexion.commit()
                
                print(f"Éxito: Cliente {id_cliente} reactivado en el sistema.")
                return True
                
            except Exception as e:
                print(f"Error al reactivar al cliente: {e}")
                conexion.rollback()
                return False
            finally:
                cursor.close()
                db.desconectar()
        return False

    @staticmethod
    def editar_cliente(id_cliente, nombres, primer_apellido, segundo_apellido, telefono, corte_preferido):
        # Edita los datos de un cliente si hubo un error al escribirlos.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = """UPDATE Clientes 
                         SET nombres = %s, primer_apellido = %s, segundo_apellido = %s, 
                             telefono = %s, corte_preferido = %s 
                         WHERE id_cliente = %s"""
                valores = (nombres, primer_apellido, segundo_apellido, telefono, corte_preferido, id_cliente)
                
                cursor.execute(sql, valores)
                conexion.commit()
                print(f"Éxito: Datos del cliente {id_cliente} actualizados correctamente.")
                return True
                
            except Exception as e:
                print(f"Error al actualizar cliente: {e}")
                conexion.rollback()
                return False
            finally:
                cursor.close()
                db.desconectar()
        return False

    @staticmethod
    def eliminar_cliente_por_error(id_cliente):
        # BORRADO FÍSICO (DELETE) con validación de seguridad.
        # Solo permite borrar al cliente si NUNCA ha comprado nada (no tiene tickets).
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
                
                # 1. Validar si el cliente ya tiene historial financiero
                cursor.execute("SELECT COUNT(*) FROM Ventas WHERE id_cliente = %s", (id_cliente,))
                tiene_ventas = cursor.fetchone()[0]
                
                if tiene_ventas > 0:
                    print(f"Alerta: No se puede borrar físicamente al cliente {id_cliente} porque tiene tickets de venta asociados.")
                    print("Por favor, utiliza la opción 'Editar' o 'Dar de baja'.")
                    return False
                
                # 2. Si no tiene ventas, procedemos con el borrado físico
                sql = "DELETE FROM Clientes WHERE id_cliente = %s"
                cursor.execute(sql, (id_cliente,))
                
                if cursor.rowcount > 0:
                    conexion.commit()
                    print(f"Éxito: Cliente {id_cliente} eliminado físicamente por error de captura.")
                    return True
                else:
                    print("Error: No se encontró el cliente.")
                    return False
                
            except Exception as e:
                print(f"Error al intentar eliminar al cliente: {e}")
                conexion.rollback()
                return False
            finally:
                cursor.close()
                db.desconectar()
        return False