from bd.conexion import ConexionDB

class Servicio:
    
    @staticmethod
    def registrar_servicio(nombre_servicio, precio_actual, duracion_minutos):
        # Validación para no permitir precios en cero o negativos
        if precio_actual <= 0:
            raise ValueError("El precio del servicio debe ser mayor a $0.")

        # Guarda un nuevo servicio de barbería en la base de datos.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = """INSERT INTO Servicios (nombre_servicio, precio_actual, duracion_minutos) 
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
        # Trae la lista completa de servicios disponibles.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True) 
                cursor.execute("SELECT * FROM Servicios ORDER BY nombre_servicio ASC")
                return cursor.fetchall()
            except Exception as e:
                print(f"Error al obtener servicios: {e}")
                return []
            finally:
                cursor.close()
                db.desconectar()
        return []

    @staticmethod
    def editar_servicio(id_servicio, nombre_servicio, precio_actual, duracion_minutos):
        # Validación para no permitir precios en cero o negativos
        if precio_actual <= 0:
            raise ValueError("El precio del servicio debe ser mayor a $0.")

        # Edita los datos del servicio (para corregir precios, duración o nombres).
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = """UPDATE Servicios 
                         SET nombre_servicio = %s, precio_actual = %s, duracion_minutos = %s 
                         WHERE id_servicio = %s"""
                valores = (nombre_servicio, precio_actual, duracion_minutos, id_servicio)
                
                cursor.execute(sql, valores)
                conexion.commit()
                print(f"Éxito: Servicio {id_servicio} actualizado correctamente.")
                return True
                
            except Exception as e:
                print(f"Error al actualizar el servicio: {e}")
                conexion.rollback()
                return False
            finally:
                cursor.close()
                db.desconectar()
        return False

    @staticmethod
    def eliminar_servicio_por_error(id_servicio):
        
        # BORRADO FÍSICO (DELETE) con validación de seguridad.
        # Solo permite borrar el servicio si NUNCA ha sido agendado en una cita ni cobrado en un ticket.
        
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
                
                # Validar si ya está en alguna cita (pasada o futura)
                cursor.execute("SELECT COUNT(*) FROM Citas WHERE id_servicio = %s", (id_servicio,))
                tiene_citas = cursor.fetchone()[0]
                
                # Validar si ya se cobró en algún ticket de venta
                cursor.execute("SELECT COUNT(*) FROM Detalle_Venta_Servicios WHERE id_servicio = %s", (id_servicio,))
                tiene_ventas = cursor.fetchone()[0]
                
                if tiene_citas > 0 or tiene_ventas > 0:
                    print(f"Alerta Crítica: No se puede borrar el servicio {id_servicio} porque ya tiene historial operativo.")
                    print(f"Detalles: {tiene_citas} citas agendadas, {tiene_ventas} tickets cobrados.")
                    print("Por favor, utiliza la opción de 'Editar' para cambiar su nombre o precio.")
                    return False
                
                # Si el servicio es nuevo y nadie lo ha usado, lo borramos físicamente
                sql = "DELETE FROM Servicios WHERE id_servicio = %s"
                cursor.execute(sql, (id_servicio,))
                
                if cursor.rowcount > 0:
                    conexion.commit()
                    print(f"Éxito: Servicio {id_servicio} eliminado físicamente por error de captura.")
                    return True
                else:
                    print("Error: No se encontró el servicio.")
                    return False
                
            except Exception as e:
                print(f"Error al intentar eliminar el servicio: {e}")
                conexion.rollback()
                return False
            finally:
                cursor.close()
                db.desconectar()
        return False