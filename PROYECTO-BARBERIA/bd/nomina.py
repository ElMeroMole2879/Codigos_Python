from bd.conexion import ConexionDB

class Nomina:

    @staticmethod
    def calcular_pago_semanal(id_empleado):
        #Calcula cuánto hay que pagarle al empleado (Salario Base + Comisiones de la semana actual).
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                
                # Obtener los datos del empleado (Salario base y % de comisión)
                sql_empleado = "SELECT nombres, salario_base, porcentaje_comision FROM Empleados WHERE id_empleado = %s"
                cursor.execute(sql_empleado, (id_empleado,))
                empleado = cursor.fetchone()
                
                if not empleado:
                    return {"error": "Empleado no encontrado"}

                salario_base = float(empleado['salario_base'])
                porcentaje = float(empleado['porcentaje_comision'])

                # Sumar todos los cortes que hizo ESTA SEMANA
                sql_servicios = """
                    SELECT SUM(ds.precio_cobrado) AS total_generado
                    FROM Detalle_Venta_Servicios ds
                    INNER JOIN Ventas v ON ds.id_venta = v.id_venta
                    WHERE ds.id_empleado = %s AND YEARWEEK(v.fecha_hora, 1) = YEARWEEK(CURDATE(), 1)
                """
                # GLOSARIO
                # ds = detalle_servicios
                # v = ventas
                cursor.execute(sql_servicios, (id_empleado,))
                resultado_servicios = cursor.fetchone()
                
                total_generado = float(resultado_servicios['total_generado']) if resultado_servicios['total_generado'] else 0.0
                
                # Calcular la matemática de la nómina
                # Si el porcentaje es 50%, multiplicamos el total generado por 0.50
                comision_ganada = total_generado * (porcentaje / 100)
                pago_total = salario_base + comision_ganada
                
                # Devolvemos un diccionario súper limpio para el frontend
                return {
                    "empleado": empleado['nombres'],
                    "salario_base": round(salario_base, 2),
                    "porcentaje_comision": f"{porcentaje}%",
                    "total_generado_a_la_barberia": round(total_generado, 2),
                    "comision_ganada": round(comision_ganada, 2),
                    "total_a_pagar": round(pago_total, 2)
                }
            # round nos ayuda a redondear los números a 2 decimales para que se vea bonito en el frontend

            except Exception as e:
                print(f"Error al calcular la nómina: {e}")
                return {"error": str(e)}
            finally:
                cursor.close()
                db.desconectar()
        return {"error": "No hay conexión a la base de datos"}