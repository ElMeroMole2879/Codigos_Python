from bd.conexion import ConexionDB

class Finanzas:

    @staticmethod
    def obtener_ingresos_detallados(periodo="dia"):
        #Calcula los ingresos totales desglosados en servicios (cortes) y productos, filtrados por periodo.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                # Glosario
                # periodo: "dia", "semana", "mes", "anio"
                # v: alias para la tabla Ventas
                # ds: alias para la tabla DETALLE_VENTA_SERVICIOS
                # dp: alias para la tabla DETALLE_VENTA_PRODUCTOS

                # Definimos el filtro de fecha según el periodo solicitado
                if periodo == "dia":
                    condicion_venta = "DATE(fecha_hora) = CURDATE()"
                    condicion_detalle = "DATE(v.fecha_hora) = CURDATE()"
                    # Nota: Usamos 'v.fecha_hora' para las tablas hijas que se unen con Ventas
                    # CURDATE() devuelve la fecha actual en MySQL, y DATE() extrae solo la parte de fecha de un DATETIME.
                elif periodo == "semana":
                    condicion_venta = "YEARWEEK(fecha_hora, 1) = YEARWEEK(CURDATE(), 1)"
                    condicion_detalle = "YEARWEEK(v.fecha_hora, 1) = YEARWEEK(CURDATE(), 1)"
                    # Nota: YEARWEEK(fecha, 1) devuelve el año y número de semana según el estándar ISO-8601, donde la semana comienza en lunes.
                elif periodo == "mes":
                    condicion_venta = "MONTH(fecha_hora) = MONTH(CURDATE()) AND YEAR(fecha_hora) = YEAR(CURDATE())"
                    condicion_detalle = "MONTH(v.fecha_hora) = MONTH(CURDATE()) AND YEAR(v.fecha_hora) = YEAR(CURDATE())"
                    # Nota: Combinamos MONTH() y YEAR() para asegurarnos de que estamos filtrando solo el mes actual del año actual.
                elif periodo == "anio":
                    condicion_venta = "YEAR(fecha_hora) = YEAR(CURDATE())"
                    condicion_detalle = "YEAR(v.fecha_hora) = YEAR(CURDATE())"
                    # Nota: YEAR() extrae el año de la fecha, permitiendo filtrar todas las ventas del año en curso.
                else:
                    return {"total_general": 0.0, "total_servicios": 0.0, "total_productos": 0.0}

                # Total general de la caja
                sql_total = f"SELECT SUM(total) AS total FROM Ventas WHERE {condicion_venta}"
                cursor.execute(sql_total)
                res_total = cursor.fetchone()
                total_general = res_total['total'] if res_total['total'] is not None else 0.0

                # Total ganado por servicios (cortes) usando la tabla hija DETALLE_VENTA_SERVICIOS
                sql_servicios = f"""
                    SELECT SUM(ds.precio_cobrado) AS total_servicios 
                    FROM DETALLE_VENTA_SERVICIOS ds
                    INNER JOIN VENTAS v ON ds.id_venta = v.id_venta
                    WHERE {condicion_detalle}
                """
                cursor.execute(sql_servicios)
                res_servicios = cursor.fetchone()
                total_servicios = res_servicios['total_servicios'] if res_servicios['total_servicios'] is not None else 0.0

                # Total ganado por productos usando la tabla hija DETALLE_VENTA_PRODUCTOS
                sql_productos = f"""
                    SELECT SUM(dp.precio_cobrado * dp.cantidad) AS total_productos 
                    FROM DETALLE_VENTA_PRODUCTOS dp
                    INNER JOIN VENTAS v ON dp.id_venta = v.id_venta
                    WHERE {condicion_detalle}
                """
                cursor.execute(sql_productos)
                res_productos = cursor.fetchone()
                total_productos = res_productos['total_productos'] if res_productos['total_productos'] is not None else 0.0

                return {
                    "total_general": float(total_general),
                    "total_servicios": float(total_servicios),
                    "total_productos": float(total_productos)
                }
                
            except Exception as e:
                print(f"Error al calcular ingresos detallados por {periodo}: {e}")
                return {"total_general": 0.0, "total_servicios": 0.0, "total_productos": 0.0}
            finally:
                cursor.close()
                db.desconectar()
        return {"total_general": 0.0, "total_servicios": 0.0, "total_productos": 0.0}