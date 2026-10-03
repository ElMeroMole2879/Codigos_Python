from bd.conexion import ConexionDB

class Cliente:
    
    @staticmethod
    def registrar_cliente(nombres, primer_apellido, segundo_apellido, telefono, corte_preferido=None):
        #Guarda un nuevo cliente en la base de datos.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
                # Actualizado con las columnas exactas de tu diagrama
                sql = """INSERT INTO CLIENTES (nombres, primer_apellido, segundo_apellido, telefono, corte_preferido) 
                         VALUES (%s, %s, %s, %s, %s)"""
                valores = (nombres, primer_apellido, segundo_apellido, telefono, corte_preferido)
                
                cursor.execute(sql, valores)
                conexion.commit() # Sellar el guardado
                print(f"Éxito: Cliente '{nombres} {primer_apellido}' registrado correctamente.")
                return True
                
            except Exception as e:
                print(f"Error al registrar cliente: {e}")
                conexion.rollback() # Cancelar transaccion si hay error
                return False
            finally:
                cursor.close()
                db.desconectar()
        return False

    @staticmethod
    def obtener_todos_los_clientes():
        #Trae la lista de clientes activos ordenados por nombre.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True) 
                # Solo trae a los clientes con activo = True
                cursor.execute("SELECT * FROM CLIENTES WHERE activo = True ORDER BY nombres ASC")
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
        #Realiza una baja lógica del cliente (activo = False) en lugar de borrarlo.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = "UPDATE CLIENTES SET activo = False WHERE id_cliente = %s"
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
        #Vuelve a activar a un cliente que había sido dado de baja.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = "UPDATE CLIENTES SET activo = True WHERE id_cliente = %s"
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