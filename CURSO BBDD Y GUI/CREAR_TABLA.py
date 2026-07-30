import mysql.connector

conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="ElMeroMole2879_",
    database="american_rider"
)

cursor = conexion.cursor()
try:
    cursor.execute("CREATE TABLE clientes" 
                   "(id INT NOT NULL AUTO_INCREMENT,"
                   "nombre VARCHAR (32) NOT NULL,"
                   "apellidos VARCHAR (64) NOT NULL,"
                   "telefono VARCHAR (9) NOT NULL,"
                   "direccion VARCHAR (256),"
                   "PRIMARY KEY (id));")
    print("Operacion exitosa")

except:
    print("Error fallo la operacion")