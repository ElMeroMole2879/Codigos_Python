from tkinter import *
from tkinter import messagebox

raiz = Tk()

#barra de menú principal

def ventanaEmergente():
    messagebox.showinfo("Ventana Emergente", "¡Hola! Soy una ventana emergente.")

def ventanaEmergenteAviso():
    messagebox.showwarning("Ventana Emergente", "¡Cuidado! Esto es una advertencia.")

def ventanaEmergentePregunta():
    respuesta = messagebox.askquestion("Ventana Emergente", "¿Quieres continuar?")
    if respuesta == "yes":
        raiz.destroy()  #cierra la ventana principal
    else:
        print("Cancelado.")

def ventanaEmergenteError():
    messagebox.askretrycancel("Ventana Emergente", "¡Error! Algo salió mal.")
    if respuesta == "retry":
        print("Reintentando...")

barraMenu = Menu(raiz)

#Creamos un menú desplegable

raiz.config(menu=barraMenu, width=300, height=300)

#Crear menús desplegables

archivoMenu = Menu(barraMenu)

#Submenús o opciones del menú desplegable Archivo

archivoMenu = Menu(barraMenu, tearoff=0)  #para que no se pueda separar el menú
archivoMenu.add_command(label="Nuevo")
archivoMenu.add_command(label="Guardar")
archivoMenu.add_separator()  #línea separadora entre opciones
archivoMenu.add_command(label="Guardar como...")
archivoMenu.add_command(label="Cerrar", command=ventanaEmergentePregunta)

archivoEditar = Menu(barraMenu)

archivoEditar = Menu(barraMenu, tearoff=0)
archivoEditar.add_command(label="Cortar", command=ventanaEmergenteAviso)
archivoEditar.add_command(label="Copiar")
archivoEditar.add_command(label="Pegar", command=ventanaEmergenteError)

archivoHerramientas = Menu(barraMenu)

archivoHerramientas = Menu(barraMenu, tearoff=0)
archivoHerramientas.add_command(label="Opciones")

archivoAyuda = Menu(barraMenu)

archivoAyuda = Menu(barraMenu, tearoff=0)
archivoAyuda.add_command(label="Acerca de...", command=ventanaEmergente)

#Añadimos opciones al menú desplegable Archivo

#barramenu.add_cascade(label="Archivo", menu=archivoMenu)
#sirve para añadir un menú desplegable a la barra de menú principal
#label es el texto que aparecerá en la barra de menú principal

barraMenu.add_cascade(label="Archivo", menu=archivoMenu)

barraMenu.add_cascade(label="Editar", menu=archivoEditar)

barraMenu.add_cascade(label="Herramientas", menu=archivoHerramientas)

barraMenu.add_cascade(label="Ayuda", menu=archivoAyuda)

raiz.mainloop()