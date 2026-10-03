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