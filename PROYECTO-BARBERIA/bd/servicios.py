from bd.conexion import ConexionDB

class Servicio:
    
    @staticmethod
    def registrar_servicio(nombre_servicio, precio_actual, duracion_minutos):
        #Guarda un nuevo servicio de barbería en la base de datos.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = """INSERT INTO SERVICIOS (nombre_servicio, precio_actual, duracion_minutos) 
                         VALUES (%s, %s, %s)"""
                valores = (nombre_servicio, precio_actual, duracion_minutos)
                
                cursor.execute(sql, valores)
                conexion.commit()
                print(f"Éxito: Servicio '{nombre_servicio}' registrado correctamente.")
                return True
                
            except Exception as e:
                print(f"Error al registrar servicio: {e}")
                conexion.rollback()
                return False
            finally:
                cursor.close()
                db.desconectar()
        return False

    @staticmethod
    def obtener_todos_los_servicios():
        #Trae la lista completa de servicios disponibles.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True) 
                cursor.execute("SELECT * FROM SERVICIOS ORDER BY nombre_servicio ASC")
                return cursor.fetchall()
            except Exception as e:
                print(f"Error al obtener servicios: {e}")
                return []
            finally:
                cursor.close()
                db.desconectar()
        return []