import bd.base_datos as sqlbd
import bd.TABLAS as tablas
base_datos = sqlbd.BaseDatos(**sqlbd.acceso_bd)

# base_datos.crear_tabla("pruebas2", "usuarios", tablas.columnas)

base_datos.eliminar_tabla("pruebas2", "usuarios")