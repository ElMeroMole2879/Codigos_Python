from bd.conexion import ConexionDB

class Cita:
    
    @staticmethod
    def agendar_cita(id_cliente, id_empleado, id_servicio, fecha_cita, hora_cita):
        #Registra una nueva cita en la base de datos. El estado será 'Pendiente' por defecto.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
                # No incluimos 'estado' en el INSERT porque la BD le pone 'Pendiente' en automático
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
        #Trae la agenda completa uniendo las tablas para mostrar texto legible en lugar de puros IDs.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True) 
                # Uso de INNER JOIN para cruzar las 4 tablas involucradas
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
                ORDER BY c.fecha_cita ASC, c.hora_cita ASC
                """
                # Glosario
                # c: Citas
                # cl: Clientes
                # e: Empleados
                # s: Servicios
                # INNER JOIN Clientes cl ON c.id_cliente = cl.id_cliente
                # Dice que de la tabla Citas (c) se va a unir con la tabla Clientes (cl) donde el id_cliente de Citas coincida con el id_cliente de Clientes.
                # SELECT SELECCIONA LOS CAMPOS QUE QUEREMOS MOSTRAR, INCLUYENDO ALIAS PARA NOMBRES MÁS CLAROS.
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
        #Cambia el estado de una cita ('Pendiente', 'Completada', 'Cancelada').
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