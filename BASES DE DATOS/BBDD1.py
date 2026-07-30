import mysql.connector

miConexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="ElMeroMole2879"
    #database="Primera_Base"        
)

miCursor = miConexion.cursor()

miCursor.execute("CREATE DATABASE IF NOT EXISTS Primera_Base")

miCursor.execute("USE Primera_Base")
miCursor.execute("""
                 CREATE TABLE IF NOT EXISTS PRODUCTOS (
                 NOMBRE_ARTICULO VARCHAR(50),
                 PRECIO INTEGER,
                 SECCION VARCHAR(20)
         )
    """)

miConexion.commit()

miCursor.close()

miConexion.close()