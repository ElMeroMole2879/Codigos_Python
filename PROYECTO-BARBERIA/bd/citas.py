from bd.conexion import ConexionDB
from datetime import datetime

class Cita:
    
    @staticmethod
    def agendar_cita(id_cliente, id_empleado, id_servicio, fecha_cita, hora_cita):
        # Validación de fecha y hora (No permitir agendar en el pasado)
        ahora = datetime.now()
        
        # Convertimos los textos que llegan desde la interfaz a objetos Date y Time reales
        try:
            fecha_dt = datetime.strptime(fecha_cita, "%Y-%m-%d").date()
            # La interfaz manda la hora con segundos (%H:%M:%S)
            hora_dt = datetime.strptime(hora_cita, "%H:%M:%S").time() 
        except ValueError:
            # Por si acaso llega en formato %H:%M
            hora_dt = datetime.strptime(hora_cita, "%H:%M").time()

        if fecha_dt < ahora.date():
            raise ValueError("No puedes agendar una cita en una fecha que ya pasó.")
        
        if fecha_dt == ahora.date() and hora_dt < ahora.time():
            raise ValueError("Esa hora ya pasó en el día de hoy.")

        # Registra una nueva cita verificando que el barbero esté disponible en ese horario.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
    
                # Revisa si el barbero ya tiene una cita 'Pendiente' o 'Completada' a esa hora.
                # Ignora las citas que fueron 'Canceladas'
                sql_disponibilidad = """
                    SELECT id_cita FROM Citas 
                    WHERE id_empleado = %s AND fecha_cita = %s AND hora_cita = %s 
                    AND estado IN ('Pendiente', 'Completada')
                """
                cursor.execute(sql_disponibilidad, (id_empleado, fecha_cita, hora_cita))
                
                if cursor.fetchone():
                    print("Error: El barbero seleccionado ya tiene una cita ocupada en ese horario.")
                    return False
                
                # Inserción de la cita
                sql = """INSERT INTO Citas (id_cliente, id_empleado, id_servicio, fecha_cita, hora_cita) 
                         VALUES (%s, %s, %s, %s, %s)"""
                valores = (id_cliente, id_empleado, id_servicio, fecha_cita, hora_cita)
                
                cursor.execute(sql, valores)
                conexion.commit()
                print(f"Éxito: Cita agendada para el {fecha_cita} a las {hora_cita}.")
                return True
                
            except Exception as e:
                print(f"Error al agendar cita: {e}")
                conexion.rollback()
                return False
            finally:
                cursor.close()
                db.desconectar()
        return False

    @staticmethod
    def obtener_todas_las_citas():
        # Trae la agenda completa uniendo las tablas para mostrar texto legible.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True) 
                sql = """
                SELECT
                    c.id_cita,
                    cl.nombres AS nombre_cliente,
                    cl.primer_apellido AS apellido_cliente,
                    cl.segundo_apellido AS segundo_apellido,
                    cl.telefono,
                    cl.corte_preferido,
                    e.nombres AS nombre_barbero,
                    s.nombre_servicio,
                    s.precio_actual,
                    c.fecha_cita,
                    c.hora_cita,
                    c.estado
                FROM Citas c
                INNER JOIN Clientes cl ON c.id_cliente = cl.id_cliente
                INNER JOIN Empleados e ON c.id_empleado = e.id_empleado
                INNER JOIN Servicios s ON c.id_servicio = s.id_servicio
                WHERE cl.activo = True AND e.activo = True
                ORDER BY c.fecha_cita ASC, c.hora_cita ASC
                """
                cursor.execute(sql)
                return cursor.fetchall()
            except Exception as e:
                print(f"Error al obtener citas: {e}")
                return []
            finally:
                cursor.close()
                db.desconectar()
        return []

    @staticmethod
    def actualizar_estado_cita(id_cita, nuevo_estado):
        # Cambia el estado de una cita ('Pendiente', 'Completada', 'Cancelada').
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = "UPDATE Citas SET estado = %s WHERE id_cita = %s"
                valores = (nuevo_estado, id_cita)
                
                cursor.execute(sql, valores)
                conexion.commit()
                print(f"Éxito: Cita {id_cita} actualizada a '{nuevo_estado}'.")
                return True
                
            except Exception as e:
                print(f"Error al actualizar estado: {e}")
                conexion.rollback()
                return False
            finally:
                cursor.close()
                db.desconectar()
        return False
        
    @staticmethod
    def eliminar_cita_por_error(id_cita):
        
        # BORRADO FÍSICO (DELETE).
        # Elimina la cita por completo de la base de datos si hubo un error de dedo al capturarla.
        
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                # Agregamos dictionary=True para poder leer por columna
                cursor = conexion.cursor(dictionary=True)
                
                # Validar el estado actual de la cita
                cursor.execute("SELECT estado FROM Citas WHERE id_cita = %s", (id_cita,))
                cita = cursor.fetchone()
                
                if cita and cita["estado"] == "Completada":
                    raise ValueError("No puedes borrar una cita que ya fue 'Completada' (ya se cobró en caja).")

                sql = "DELETE FROM Citas WHERE id_cita = %s"
                cursor.execute(sql, (id_cita,))
                
                # rowcount nos dice cuántos registros se vieron afectados por el DELETE
                if cursor.rowcount > 0:
                    conexion.commit()
                    print(f"Éxito: Cita {id_cita} eliminada físicamente (borrado seguro).")
                    return True
                else:
                    print(f"Error: No se encontró la cita {id_cita} para eliminar.")
                    return False
                
            except Exception as e:
                print(f"Error al intentar eliminar la cita: {e}")
                conexion.rollback()
                # Si el error es un ValueError (nuestra validación), lo volvemos a lanzar hacia Tkinter
                if isinstance(e, ValueError):
                    raise e
                return False
            finally:
                cursor.close()
                db.desconectar()
        return False