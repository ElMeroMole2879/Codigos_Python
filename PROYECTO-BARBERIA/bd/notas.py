from bd.conexion import ConexionDB
from datetime import datetime

class Nota:

    @staticmethod
    def agregar_nota(id_cliente, id_empleado, descripcion):
        # Crea una nueva anotación sobre las preferencias o detalles del cliente
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
                # Usamos date en lugar de datetime para que coincida con tu columna 'fecha_nota DATE'
                fecha_nota = datetime.now().strftime('%Y-%m-%d')
                
                # Modificado a Notas_Historial_Cliente
                sql = """INSERT INTO Notas_Historial_Cliente (id_cliente, id_empleado, fecha_nota, descripcion) 
                         VALUES (%s, %s, %s, %s)"""
                valores = (id_cliente, id_empleado, fecha_nota, descripcion)
                
                cursor.execute(sql, valores)
                conexion.commit()
                print(f"Éxito: Nota agregada al expediente del cliente {id_cliente}.")
                return True
                
            except Exception as e:
                print(f"Error al agregar la nota: {e}")
                conexion.rollback()
                return False
            finally:
                cursor.close()
                db.desconectar()
        return False

    @staticmethod
    def obtener_notas_cliente(id_cliente):
        # Trae todo el historial de notas de un cliente ordenado de la más reciente a la más antigua
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                
                # Modificado a Notas_Historial_Cliente
                sql = """
                    SELECT n.id_nota, n.fecha_nota, n.descripcion, e.nombres AS escrito_por
                    FROM Notas_Historial_Cliente n
                    INNER JOIN Empleados e ON n.id_empleado = e.id_empleado
                    WHERE n.id_cliente = %s
                    ORDER BY n.fecha_nota DESC
                """
                cursor.execute(sql, (id_cliente,))
                return cursor.fetchall()
                
            except Exception as e:
                print(f"Error al obtener las notas: {e}")
                return []
            finally:
                cursor.close()
                db.desconectar()
        return []

    @staticmethod
    def editar_nota(id_nota, nueva_descripcion):
        #Permite corregir faltas de ortografía o detalles en una nota existente.
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = "UPDATE Notas_Historial_Cliente SET descripcion = %s WHERE id_nota = %s"
                cursor.execute(sql, (nueva_descripcion, id_nota))
                
                if cursor.rowcount > 0:
                    conexion.commit()
                    print(f"Éxito: Nota {id_nota} actualizada correctamente.")
                    return True
                else:
                    print(f"Error: No se encontró la nota {id_nota}.")
                    return False
                    
            except Exception as e:
                print(f"Error al actualizar la nota: {e}")
                conexion.rollback()
                return False
            finally:
                cursor.close()
                db.desconectar()
        return False

    @staticmethod
    def eliminar_nota_por_error(id_nota):
        
        # BORRADO FÍSICO (DELETE).
        # Elimina la nota permanentemente si se asignó al cliente equivocado o fue un error grave.
        
        db = ConexionDB()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = "DELETE FROM Notas_Historial_Cliente WHERE id_nota = %s"
                cursor.execute(sql, (id_nota,))
                
                if cursor.rowcount > 0:
                    conexion.commit()
                    print(f"Éxito: Nota {id_nota} eliminada físicamente (borrado seguro).")
                    return True
                else:
                    print(f"Error: No se encontró la nota {id_nota} para eliminar.")
                    return False
                    
            except Exception as e:
                print(f"Error al intentar eliminar la nota: {e}")
                conexion.rollback()
                return False
            finally:
                cursor.close()
                db.desconectar()
        return False