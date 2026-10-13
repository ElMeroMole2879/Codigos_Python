from bd.conexion import ConexionDB
from datetime import date

class Reporte:

    @staticmethod
    def obtener_corte_caja_diario(fecha=None):
        # Calcula el total vendido en un día, separado por método de pago.
        # Si no se le pasa una fecha, hace el corte del día de hoy automáticamente.
        # Si el administrador no elige una fecha en el calendario, usamos la de hoy
        if fecha is None:
            fecha = date.today().strftime('%Y-%m-%d')

        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                
                # Obtener el resumen por método de pago (Efectivo, Tarjeta, Transferencia)
                # DATE(fecha_hora) extrae solo la fecha (año-mes-día) e ignora la hora del ticket
                sql_pagos = """
                    SELECT metodo_pago, SUM(total) as total_recaudado, COUNT(id_venta) as numero_tickets
                    FROM Ventas 
                    WHERE DATE(fecha_hora) = %s
                    GROUP BY metodo_pago
                """
                cursor.execute(sql_pagos, (fecha,))
                desglose_pagos = cursor.fetchall()

                # Obtener el Gran Total de todo el día
                sql_total = """
                    SELECT SUM(total) as gran_total 
                    FROM Ventas 
                    WHERE DATE(fecha_hora) = %s
                """
                cursor.execute(sql_total, (fecha,))
                resultado_total = cursor.fetchone()
                
                # Si no hubo ventas, evitamos que regrese "None" y ponemos 0.0
                gran_total = float(resultado_total['gran_total']) if resultado_total['gran_total'] else 0.0

                # Empaquetamos todo en un diccionario súper limpio para el frontend
                return {
                    "fecha_corte": fecha,
                    "desglose_por_metodo": desglose_pagos,
                    "gran_total_del_dia": round(gran_total, 2)
                }

            except Exception as e:
                print(f"Error al generar el corte de caja: {e}")
                return {"error": str(e)}
            finally:
                cursor.close()
                db.desconectar()
        return {"error": "No hay conexión a la base de datos"}