import mysql.connector
from bd.conexion import ConexionDB 

class Usuario:
    def validar_login(self, username, password):
        # Conexión a la base de datos
        db = ConexionDB()
        conexion = db.conectar()

        # Si la conexión falla, retornamos None
        if conexion is None:
            print("No se pudo establecer conexión con la base de datos.")
            return None

        try:
            # Usamos dictionary=True para que en vez de una tupla confusa (1, 'Axel'), 
            # nos devuelva algo fácil de leer: {'id_usuario': 1, 'nombres': 'Axel'}
            cursor = conexion.cursor(dictionary=True)

            # Consulta SQL SEGURA. Usamos %s para evitar ataques de SQL Injection
            # % lo lee como texto no como código SQL, y mysql.connector se encarga de reemplazarlo con la variable correspondiente
            sql = """
                SELECT id_usuario, nombres, primer_apellido, rol, activo 
                FROM Usuarios 
                WHERE username = %s AND password = %s
            """
            
            # MySQL intercambia de forma segura los %s por las variables de esta tupla
            cursor.execute(sql, (username, password))
            usuario = cursor.fetchone() # Trae el primer resultado de la consulta, o None si no hay resultados

            # Lógica de validación
            if usuario:
                if usuario['activo'] == 1: # 1 = True, 0 = False
                    # Si el login es exitoso, actualizamos su campo de "ultimo_acceso"
                    sql_update = "UPDATE Usuarios SET ultimo_acceso = NOW() WHERE id_usuario = %s"
                    cursor.execute(sql_update, (usuario['id_usuario'],))
                    conexion.commit()
                    
                    return usuario # Retornamos sus datos para que Tkinter sepa quién entró
                else:
                    return "INACTIVO" # Existe, pero fue dado de baja
            else:
                return None # Las credenciales no coinciden

        except mysql.connector.Error as e:
            print(f"Error al validar login: {e}")
            return None
            
        finally:
            # Siempre cerramos la conexión para no saturar el servidor
            if conexion.is_connected():
                cursor.close()
                db.desconectar()