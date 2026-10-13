from bd.conexion import ConexionDB

class Empleado:

    @staticmethod
    def registrar_empleado(nombres, primer_apellido, segundo_apellido, curp, telefono, correo, 
                           calle, num_exterior, num_interior, colonia, cp, puesto, 
                           salario_base=0.0, porcentaje_comision=0.0):
        #Registra un nuevo empleado en el sistema.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = """INSERT INTO Empleados 
                         (nombres, primer_apellido, segundo_apellido, curp, telefono, correo, 
                          calle, num_exterior, num_interior, colonia, cp, puesto, salario_base, porcentaje_comision) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                
                valores = (nombres, primer_apellido, segundo_apellido, curp, telefono, correo, 
                           calle, num_exterior, num_interior, colonia, cp, puesto, salario_base, porcentaje_comision)
                
                cursor.execute(sql, valores)
                conexion.commit()
                print(f"Éxito: Empleado '{nombres} {primer_apellido}' registrado correctamente.")
                return True
                
            except Exception as e:
                print(f"Error al registrar empleado: {e}")
                conexion.rollback()
                return False
            finally:
                cursor.close()
                db.desconectar()
        return False

    @staticmethod
    def dar_de_baja(id_empleado):
        #Realiza una baja lógica del empleado (activo = False) en lugar de borrarlo.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
                # En lugar de DELETE, actualizamos el estado
                sql = "UPDATE Empleados SET activo = False WHERE id_empleado = %s"
                cursor.execute(sql, (id_empleado,))
                conexion.commit()
                
                print(f"Éxito: Empleado {id_empleado} dado de baja del sistema.")
                return True
                
            except Exception as e:
                print(f"Error al dar de baja al empleado: {e}")
                conexion.rollback()
                return False
            finally:
                cursor.close()
                db.desconectar()
        return False

    @staticmethod
    def obtener_empleados_activos():
        #Trae solo a los empleados que siguen trabajando en la barbería.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                # Filtramos para que no salgan los que ya fueron dados de baja
                cursor.execute("SELECT * FROM Empleados WHERE activo = True ORDER BY nombres ASC")
                return cursor.fetchall()
            except Exception as e:
                print(f"Error al obtener empleados: {e}")
                return []
            finally:
                cursor.close()
                db.desconectar()
        return []

    @staticmethod
    def editar_empleado(id_empleado, nombres, primer_apellido, segundo_apellido, curp, telefono, correo, 
                        calle, num_exterior, num_interior, colonia, cp, puesto, 
                        salario_base, porcentaje_comision):
        
        # Corrige los datos de un empleado si hubo un error de captura.

        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = """UPDATE Empleados 
                         SET nombres = %s, primer_apellido = %s, segundo_apellido = %s, curp = %s, 
                             telefono = %s, correo = %s, calle = %s, num_exterior = %s, num_interior = %s, 
                             colonia = %s, cp = %s, puesto = %s, salario_base = %s, porcentaje_comision = %s 
                         WHERE id_empleado = %s"""
                valores = (nombres, primer_apellido, segundo_apellido, curp, telefono, correo, 
                           calle, num_exterior, num_interior, colonia, cp, puesto, 
                           salario_base, porcentaje_comision, id_empleado)
                
                cursor.execute(sql, valores)
                conexion.commit()
                print(f"Éxito: Datos del empleado {id_empleado} actualizados correctamente.")
                return True
                
            except Exception as e:
                print(f"Error al actualizar empleado: {e}")
                conexion.rollback()
                return False
            finally:
                cursor.close()
                db.desconectar()
        return False

    @staticmethod
    def eliminar_empleado_por_error(id_empleado):
        
        # BORRADO FÍSICO (DELETE) con máxima validación.
        # Comprueba que el empleado no tenga citas, ventas ni notas antes de borrarlo.
        # Si tiene historial operativo, no se permite el borrado y se sugiere dar de baja.

        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
                
                # Validar Citas
                cursor.execute("SELECT COUNT(*) FROM Citas WHERE id_empleado = %s", (id_empleado,))
                tiene_citas = cursor.fetchone()[0]
                
                # Validar Servicios en Tickets
                cursor.execute("SELECT COUNT(*) FROM Detalle_Venta_Servicios WHERE id_empleado = %s", (id_empleado,))
                tiene_servicios = cursor.fetchone()[0]
                
                # Validar Notas de Historial
                cursor.execute("SELECT COUNT(*) FROM Notas_Historial_Cliente WHERE id_empleado = %s", (id_empleado,))
                tiene_notas = cursor.fetchone()[0]
                
                # Si el empleado ya hizo ALGO operativo, bloqueamos el borrado
                if tiene_citas > 0 or tiene_servicios > 0 or tiene_notas > 0:
                    print(f"Alerta Crítica: No se puede borrar al empleado {id_empleado} porque tiene historial operativo.")
                    print(f"Detalles: {tiene_citas} citas, {tiene_servicios} servicios cobrados, {tiene_notas} notas escritas.")
                    print("Por favor, utiliza la opción 'Dar de baja'.")
                    return False
                
                # Si está completamente limpio, procedemos a borrar
                sql = "DELETE FROM Empleados WHERE id_empleado = %s"
                cursor.execute(sql, (id_empleado,))
                
                if cursor.rowcount > 0:
                    conexion.commit()
                    print(f"Éxito: Empleado {id_empleado} eliminado físicamente (borrado seguro).")
                    return True
                else:
                    print("Error: No se encontró el empleado.")
                    return False
                
            except Exception as e:
                print(f"Error al intentar eliminar al empleado: {e}")
                conexion.rollback()
                return False
            finally:
                cursor.close()
                db.desconectar()
        return False