import mysql.connector

# CONECTAR BASE DE DATOS

conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="ElMeroMole2879_",
    database="world"
)

# CREAMOS EL CURSOR
cursor = conexion.cursor()

# EJECUTAMOS CONSULTA
cursor.execute("SELECT Name, Population FROM City LIMIT 5")

# cursor.fetchall() para obtener resultados
resultados = cursor.fetchall()

print(resultados)

for i in resultados:
    print(i)

# SE PUEDE OBTENER DE LAS 2 MANERAS

cursor.close()
conexion.close()