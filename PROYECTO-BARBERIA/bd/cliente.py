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
        #Trae la lista completa de clientes ordenados por nombre.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True) 
                cursor.execute("SELECT * FROM CLIENTES ORDER BY nombres ASC")
                return cursor.fetchall()
            except Exception as e:
                print(f"Error al obtener clientes: {e}")
                return []
            finally:
                cursor.close()
                db.desconectar()
        return []