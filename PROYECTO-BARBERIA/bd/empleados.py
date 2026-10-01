from bd.conexion import ConexionDB

class Empleado:
    
    @staticmethod
    def registrar_empleado(nombres, primer_apellido, segundo_apellido, curp, telefono, correo, 
                           calle, num_exterior, num_interior, colonia, cp, puesto, 
                           salario_base=0.00, porcentaje_comision=0.00):
        #Registra un nuevo empleado (barbero o recepcionista) en el sistema.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                # %s sirve como marcador de posición para los valores que se insertarán en la base de datos.
                # ejemplo %s es 1 y el siguiente %s es 2, y así sucesivamente. Esto ayuda a prevenir inyecciones SQL.
                cursor = conexion.cursor()
                sql = """INSERT INTO Empleados 
                         (nombres, primer_apellido, segundo_apellido, curp, telefono, correo, 
                          calle, num_exterior, num_interior, colonia, cp, puesto, 
                          salario_base, porcentaje_comision) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                
                valores = (nombres, primer_apellido, segundo_apellido, curp, telefono, correo, 
                           calle, num_exterior, num_interior, colonia, cp, puesto, 
                           salario_base, porcentaje_comision)
                
                cursor.execute(sql, valores)
                conexion.commit()
                print(f"Éxito: Empleado '{nombres} {primer_apellido}' registrado bajo el puesto de '{puesto}'.")
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
    def obtener_todos_los_empleados():
        """Trae la lista del personal que se encuentra activo actualmente."""
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True) 
                cursor.execute("SELECT * FROM Empleados WHERE activo = TRUE ORDER BY nombres ASC")
                return cursor.fetchall()
            except Exception as e:
                print(f"Error al obtener empleados: {e}")
                return []
            finally:
                cursor.close()
                db.desconectar()
        return []