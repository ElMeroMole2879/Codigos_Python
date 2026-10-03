from bd.conexion import ConexionDB

class HistorialCliente:

    @staticmethod
    def obtener_tickets(id_cliente):
        #Devuelve el historial de compras y servicios pagados en la tabla VENTAS.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                sql = """
                    SELECT id_venta, fecha_hora, total, metodo_pago 
                    FROM Ventas 
                    WHERE id_cliente = %s 
                    ORDER BY fecha_hora DESC
                """
                cursor.execute(sql, (id_cliente,))
                return cursor.fetchall()
            except Exception as e:
                print(f"Error al obtener tickets del cliente: {e}")
                return []
            finally:
                cursor.close()
                db.desconectar()
        return []

    @staticmethod
    def obtener_citas_pasadas(id_cliente):
        #Devuelve el historial de citas (completadas o canceladas) uniendo datos de Servicios y Empleados.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                sql = """
                    SELECT c.fecha_cita, c.hora_cita, c.estado, s.nombre_servicio, e.nombres AS barbero 
                    FROM Citas c
                    INNER JOIN Servicios s ON c.id_servicio = s.id_servicio
                    INNER JOIN Empleados e ON c.id_empleado = e.id_empleado
                    WHERE c.id_cliente = %s 
                    ORDER BY c.fecha_cita DESC, c.hora_cita DESC
                """
                # GLOSARIO
                # c = citas
                # s = servicios
                # e = empleados

                cursor.execute(sql, (id_cliente,))
                return cursor.fetchall()
            except Exception as e:
                print(f"Error al obtener historial de citas: {e}")
                return []
            finally:
                cursor.close()
                db.desconectar()
        return []

    @staticmethod
    def obtener_notas_medicas_esteticas(id_cliente):
        #Devuelve las observaciones dejadas por los barberos en la tabla NOTAS_HISTORIAL_CLIENTE.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                sql = """
                    SELECT n.fecha_nota, n.descripcion, e.nombres AS barbero_que_anoto 
                    FROM Notas_Historial_Cliente n
                    INNER JOIN Empleados e ON n.id_empleado = e.id_empleado
                    WHERE n.id_cliente = %s 
                    ORDER BY n.fecha_nota DESC
                """
                #
                cursor.execute(sql, (id_cliente,))
                return cursor.fetchall()
            except Exception as e:
                print(f"Error al obtener notas del cliente: {e}")
                return []
            finally:
                cursor.close()
                db.desconectar()
        return []

class HistorialEmpleado:

    @staticmethod
    def obtener_citas_atendidas(id_empleado):
        #Devuelve el historial de todas las citas que ha atendido un barbero.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                sql = """
                    SELECT c.fecha_cita, c.hora_cita, c.estado, s.nombre_servicio, 
                           cl.nombres AS nombre_cliente, cl.primer_apellido AS apellido_cliente
                    FROM Citas c
                    INNER JOIN Servicios s ON c.id_servicio = s.id_servicio
                    INNER JOIN Clientes cl ON c.id_cliente = cl.id_cliente
                    WHERE c.id_empleado = %s 
                    ORDER BY c.fecha_cita DESC, c.hora_cita DESC
                """
                # GLOSARIO
                # c = citas
                # s = servicios
                # cl = clientes
                cursor.execute(sql, (id_empleado,))
                return cursor.fetchall()
            except Exception as e:
                print(f"Error al obtener citas del empleado: {e}")
                return []
            finally:
                cursor.close()
                db.desconectar()
        return []

    @staticmethod
    def obtener_servicios_cobrados(id_empleado, periodo="mes"):
        #Devuelve los servicios realizados por el barbero para calcular sus comisiones.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                
                # Filtro por periodo para saber de cuándo calcular la comisión
                if periodo == "semana":
                    filtro_fecha = "YEARWEEK(v.fecha_hora, 1) = YEARWEEK(CURDATE(), 1)"
                elif periodo == "mes":
                    filtro_fecha = "MONTH(v.fecha_hora) = MONTH(CURDATE()) AND YEAR(v.fecha_hora) = YEAR(CURDATE())"
                else:
                    filtro_fecha = "1=1" # Trae todo el historial histórico

                sql = f"""
                    SELECT v.fecha_hora, s.nombre_servicio, ds.precio_cobrado 
                    FROM Detalle_Venta_Servicios ds
                    INNER JOIN Ventas v ON ds.id_venta = v.id_venta
                    INNER JOIN Servicios s ON ds.id_servicio = s.id_servicio
                    WHERE ds.id_empleado = %s AND {filtro_fecha}
                    ORDER BY v.fecha_hora DESC
                """
                # GLOSARIO
                # v = ventas
                # ds = detalle_servicios
                # s = servicios
                cursor.execute(sql, (id_empleado,))
                return cursor.fetchall()
            except Exception as e:
                print(f"Error al obtener servicios cobrados del empleado: {e}")
                return []
            finally:
                cursor.close()
                db.desconectar()
        return []