from bd.conexion import ConexionDB

class Finanzas:

    @staticmethod
    def obtener_ingresos_detallados(periodo="dia"):

        #Calcula los ingresos totales desglosados en servicios y productos, filtrados por periodo.

        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)

                # Definimos el filtro de fecha según el periodo solicitado
                if periodo == "dia":
                    condicion_venta = "DATE(fecha_hora) = CURDATE()"
                    condicion_detalle = "DATE(v.fecha_hora) = CURDATE()"
                elif periodo == "semana":
                    condicion_venta = "YEARWEEK(fecha_hora, 1) = YEARWEEK(CURDATE(), 1)"
                    condicion_detalle = "YEARWEEK(v.fecha_hora, 1) = YEARWEEK(CURDATE(), 1)"
                elif periodo == "mes":
                    condicion_venta = "MONTH(fecha_hora) = MONTH(CURDATE()) AND YEAR(fecha_hora) = YEAR(CURDATE())"
                    condicion_detalle = "MONTH(v.fecha_hora) = MONTH(CURDATE()) AND YEAR(v.fecha_hora) = YEAR(CURDATE())"
                elif periodo == "anio":
                    condicion_venta = "YEAR(fecha_hora) = YEAR(CURDATE())"
                    condicion_detalle = "YEAR(v.fecha_hora) = YEAR(CURDATE())"
                else:
                    return {"total_general": 0.0, "total_servicios": 0.0, "total_productos": 0.0}

                # Total general de la caja
                sql_total = f"SELECT SUM(total) AS total FROM Ventas WHERE {condicion_venta}"
                cursor.execute(sql_total)
                res_total = cursor.fetchone()
                total_general = res_total['total'] if res_total['total'] is not None else 0.0

                # Total ganado por servicios (cortes) usando la tabla hija Detalle_Venta_Servicios
                sql_servicios = f"""
                    SELECT SUM(ds.precio_cobrado) AS total_servicios 
                    FROM Detalle_Venta_Servicios ds
                    INNER JOIN Ventas v ON ds.id_venta = v.id_venta
                    WHERE {condicion_detalle}
                """
                cursor.execute(sql_servicios)
                res_servicios = cursor.fetchone()
                total_servicios = res_servicios['total_servicios'] if res_servicios['total_servicios'] is not None else 0.0

                # Total ganado por productos usando la tabla hija Detalle_Venta_Productos
                sql_productos = f"""
                    SELECT SUM(dp.precio_cobrado * dp.cantidad) AS total_productos 
                    FROM Detalle_Venta_Productos dp
                    INNER JOIN Ventas v ON dp.id_venta = v.id_venta
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

    @staticmethod
    def obtener_ingresos_por_rango(fecha_inicio, fecha_fin):
        
        # Consulta de ingresos para un bloque de días exacto
        # Formatos esperados: 'YYYY-MM-DD'
        
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                
                # Resumen de Ventas
                sql = """
                    SELECT 
                        SUM(total) AS gran_total,
                        COUNT(id_venta) AS total_tickets
                    FROM Ventas
                    WHERE DATE(fecha_hora) BETWEEN %s AND %s
                """
                cursor.execute(sql, (fecha_inicio, fecha_fin))
                resumen = cursor.fetchone()
                
                gran_total = float(resumen['gran_total']) if resumen['gran_total'] else 0.0
                tickets = resumen['total_tickets'] if resumen['total_tickets'] else 0
                
                return {
                    "fecha_inicio": fecha_inicio,
                    "fecha_fin": fecha_fin,
                    "gran_total": gran_total,
                    "cantidad_tickets": tickets
                }
                
            except Exception as e:
                print(f"Error al calcular ingresos por rango: {e}")
                return None
            finally:
                cursor.close()
                db.desconectar()
        return None