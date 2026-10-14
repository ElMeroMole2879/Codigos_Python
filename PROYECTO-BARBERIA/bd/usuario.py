import mysql.connector
from bd.conexion import ConexionDB 

class Usuario:
    
    @staticmethod
    def validar_login(username, password):
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
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                db.desconectar()

    @staticmethod
    def registrar_usuario(nombres, primer_apellido, segundo_apellido, username, password, rol):
        # Crea una nueva cuenta de acceso al sistema (Dueño o Recepcionista).
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = """INSERT INTO Usuarios (nombres, primer_apellido, segundo_apellido, username, password, rol) 
                         VALUES (%s, %s, %s, %s, %s, %s)"""
                valores = (nombres, primer_apellido, segundo_apellido, username, password, rol)
                
                cursor.execute(sql, valores)
                conexion.commit()
                print(f"Éxito: Cuenta de usuario '{username}' creada correctamente.")
                return True
                
            except mysql.connector.Error as e:
                # Error 1062 significa entrada duplicada (username ya existe)
                if e.errno == 1062:
                    print("Error: El nombre de usuario (username) ya está en uso. Elige otro.")
                else:
                    print(f"Error al registrar usuario: {e}")
                conexion.rollback()
                return False
            finally:
                cursor.close()
                db.desconectar()
        return False

    @staticmethod
    def obtener_todos_los_usuarios():
        # Trae la lista de todos los usuarios del sistema (activos e inactivos).
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True) 
                # No mostramos el password por seguridad
                cursor.execute("""
                    SELECT id_usuario, nombres, primer_apellido, segundo_apellido, username, rol, activo, ultimo_acceso 
                    FROM Usuarios ORDER BY nombres ASC
                """)
                return cursor.fetchall()
            except Exception as e:
                print(f"Error al obtener usuarios: {e}")
                return []
            finally:
                cursor.close()
                db.desconectar()
        return []

    @staticmethod
    def cambiar_estado(id_usuario, estado_activo):
        # Activa (True) o desactiva (False) la cuenta de un usuario para que no pueda loguearse.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = "UPDATE Usuarios SET activo = %s WHERE id_usuario = %s"
                cursor.execute(sql, (estado_activo, id_usuario))
                conexion.commit()
                estado_str = "activado" if estado_activo else "desactivado (baja lógica)"
                print(f"Éxito: Usuario {id_usuario} ha sido {estado_str}.")
                return True
                
            except Exception as e:
                print(f"Error al cambiar estado del usuario: {e}")
                conexion.rollback()
                return False
            finally:
                cursor.close()
                db.desconectar()
        return False

    @staticmethod
    def editar_usuario(id_usuario, nombres, primer_apellido, segundo_apellido, rol):
        # Permite corregir el nombre o cambiar el rol de un usuario.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = """UPDATE Usuarios 
                         SET nombres = %s, primer_apellido = %s, segundo_apellido = %s, rol = %s 
                         WHERE id_usuario = %s"""
                valores = (nombres, primer_apellido, segundo_apellido, rol, id_usuario)
                
                cursor.execute(sql, valores)
                conexion.commit()
                print(f"Éxito: Datos del usuario {id_usuario} actualizados.")
                return True
                
            except Exception as e:
                print(f"Error al editar usuario: {e}")
                conexion.rollback()
                return False
            finally:
                cursor.close()
                db.desconectar()
        return False

    @staticmethod
    def eliminar_usuario_por_error(id_usuario):
        
        # BORRADO FÍSICO (DELETE) con validación estricta de seguridad.
        # Solo se puede borrar la cuenta si el usuario NUNCA ha cobrado un ticket en la tabla Ventas.
        
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
                
                # Protección contra auto-eliminación o borrado del admin principal
                # Opcional, pero recomendado: No dejar que borren el usuario con ID 1
                if id_usuario == 1:
                    print("Error Crítico: El usuario administrador principal no puede ser eliminado físicamente.")
                    return False

                # Validar si ya cobró tickets en la caja registradora
                cursor.execute("SELECT COUNT(*) FROM Ventas WHERE id_usuario = %s", (id_usuario,))
                tiene_ventas = cursor.fetchone()[0]
                
                if tiene_ventas > 0:
                    print(f"Alerta de Auditoría: No se puede borrar físicamente al usuario {id_usuario} porque ya operó la caja (tiene tickets de venta asociados).")
                    print("Por favor, utiliza la opción 'Cambiar Estado' para desactivar su cuenta.")
                    return False
                
                # Si está limpio (error de dedo al crearlo), lo destruimos de la BD
                sql = "DELETE FROM Usuarios WHERE id_usuario = %s"
                cursor.execute(sql, (id_usuario,))
                
                if cursor.rowcount > 0:
                    conexion.commit()
                    print(f"Éxito: Cuenta de usuario {id_usuario} eliminada físicamente de la base de datos.")
                    return True
                else:
                    print("Error: No se encontró el usuario.")
                    return False
                
            except Exception as e:
                print(f"Error al intentar eliminar la cuenta de usuario: {e}")
                conexion.rollback()
                return False
            finally:
                cursor.close()
                db.desconectar()
        return False