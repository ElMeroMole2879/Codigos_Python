import mysql.connector
import tkinter as tk
from tkinter import ttk
# CONECTAR BASE DE DATOS

def mostrar_ciudades():
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
    conexion.close()

    for row in resultados:
        tabla.insert("", "end", values=row)

# CONFIGURAR VENTANA
root = tk.Tk()
root.title("Ciudades del Mundo")

tabla = ttk.Treeview(root, columns=("Ciudad", "Poblacion"), show="headings")
tabla.heading("Ciudad", text="Ciudad")
tabla.heading("Poblacion", text="Poblacion")
tabla.pack()

btn = tk.Button(root, text="Mostrar Ciudades", command=mostrar_ciudades)
btn.pack()

root.mainloop()