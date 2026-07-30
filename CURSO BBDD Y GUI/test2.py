import mysql.connector

conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="ElMeroMole2879_",
)

cursor = conexion.cursor()
try:
    cursor.execute("DROP DATABASE pruebas2;")
    print("Operacion exitosa")

except:
    print("Error fallo la operacion")