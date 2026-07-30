import mysql.connector
import os
import subprocess
import datetime

# CONEXION A BASE DE DATOS
acceso_bd = {"host" : "localhost",
             "user" : "root",
             "password" : "ElMeroMole2879_",
             }

# --> RUTAS

# RAIZ DE LA CARPETA DEL PROYECTO
carpeta_principal = os.path.dirname(__file__)

carpeta_respaldo = os.path.join(carpeta_principal, "respaldo")

class BaseDatos:
    #CONEXION Y CURSOR
    def __init__(self, **kwargs):
        self.conector = mysql.connector.connect(**kwargs)
        self.cursor = self.conector.cursor()
        self.contrasena = kwargs["password"]

    # DECORADOR PARA EL REPORTE DE BASES DE DATOS EN EL SERVIDOR

    def reporte_bd(funcion_parametro):
        def interno(self, nombre_bd):
            funcion_parametro(self, nombre_bd)
            print("Estas son las bases de datos que tiene el servidor:")
            BaseDatos.mostrar_bd(self)
        return interno
    
    #ASI FUNCIONA UN DECORADOR

    # def decorador(func):
        #def envoltura():
            #print("Antes de ejecutar la función")

            #func()

            #print("Después de ejecutar la función")

        #return envoltura

    # HACE UNA CONSULTA CUALQUIERA AL SERVIDOR

    def consulta(self, sql):
        self.cursor.execute(sql)
        return self.cursor
    
    # MUESTRA LAS BASES DE DATOS DEL SERVIDOS

    def mostrar_bd(self):
        self.cursor.execute("SHOW DATABASES")
        for i in self.cursor:
            print(i)

    # ELIMINA LA BASE DE DATOS
    @reporte_bd
    def eliminar_bd(self, nombre_bd):
        try:
            self.cursor.execute(f"DROP DATABASE {nombre_bd}")
            print(f"Se elimino la base de datos {nombre_bd} correctamente")

        except:
            print(f"Base de datos {nombre_bd} no encontrada")

    # CREA UNA BASE DE DATOS
    @reporte_bd
    def crear_bd(self, nombre_bd):
        try:
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {nombre_bd}")
            print(f"Se creo la base de datos {nombre_bd} correctamente")

        except:
            print(f"Ocurrio un error al crear la base de datos {nombre_bd}")

    #CREAR BACKUPS DE BASES DE DATOS
    def copia_bd(self, nombre_bd):
        #OBTIENE LA FECHA Y HORA ACTUAL
        fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        #CREA EL ARCHIVO DE RESPALDO CARPETA, NOMBRE Y FECHA HORA ES EL NOMBRE DEL ARCHIVO
        with open(f'{carpeta_respaldo}/{nombre_bd}_{fecha_hora}.sql', 'w') as out:
            subprocess.Popen(f'"C:\Program Files\MySQL\MySQL Workbench 8.0 CE\mysqldump.exe" --user=root --password={self.contrasena} --databases {nombre_bd}', shell=True,
                                    stdout=out)

    def crear_tabla(self, nombre_bd, nombre_tabla, columnas):
        # STRING PARA GUARDAR EL STRING CON LAS COLUMNAS Y TIPOS DE DATOS 
        columnas_string = ""
        # ITERA SOBRE EL DICCIONARIO DE COLUMNAS Y TIPOS DE DATOS
        for columna in columnas:
            # FORMAMOS EL STRING  CON NOMBRE, TIPO Y LONGITUD DE CADA COLUMNA
            columnas_string += f"{columna['name']} {columna['type']}({columna['length']})"
            # EJEMPLO DE +=
            # A = "AXEL"
            # A += " PEREZ"
            # A = "AXELPEREZ"
            # SI ES CLAVE PRIMRARIA, AUTO_INCREMENT O NOT_NULL, SE AGREGA AL STRING
            if columna['primary_key']:
                columnas_string += " PRIMARY KEY"
            if columna['auto_increment']:
                columnas_string += " AUTO_INCREMENT"
            if columna['not_null']:
                columnas_string += " NOT NULL"
            # HACE UN SALTO DE LINEA PARA CADA COLUMNA
            columnas_string += ",\n"
            # ELIMINA LA ULTIMA COMA Y SALTO DE LINEA
        columnas_string = columnas_string[:-2]

        # LE INDICA QUE BASE DE DATOS USAR
        self.cursor.execute(f"USE {nombre_bd}")
        # CREA LA TABLA CON EL STRING DE COLUMNAS Y TIPOS DE DATOS
        sql = f"CREATE TABLE IF NOT EXISTS {nombre_tabla} ({columnas_string});"
        # EJECUTA EL SQL PARA CREAR LA TABLA
        self.cursor.execute(sql)
        # SE CONFIRMA LA CREACION DE LA TABLA
        self.conector.commit()
        # SE CIERRA LA CONEXION A LA BASE DE DATOS
        self.cursor.close()

    def eliminar_tabla(self, nombre_bd, nombre_tabla):
        self.cursor.execute(f"USE {nombre_bd}")
        self.cursor.execute(f"DROP TABLE IF EXISTS {nombre_tabla}")