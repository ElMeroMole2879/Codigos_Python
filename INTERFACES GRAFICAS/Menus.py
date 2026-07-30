from tkinter import *

raiz = Tk()

#barra de menú principal

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
archivoMenu.add_command(label="Cerrar")

archivoEditar = Menu(barraMenu)

archivoEditar = Menu(barraMenu, tearoff=0)
archivoEditar.add_command(label="Cortar")
archivoEditar.add_command(label="Copiar")
archivoEditar.add_command(label="Pegar")

archivoHerramientas = Menu(barraMenu)

archivoHerramientas = Menu(barraMenu, tearoff=0)
archivoHerramientas.add_command(label="Opciones")

archivoAyuda = Menu(barraMenu)

archivoAyuda = Menu(barraMenu, tearoff=0)
archivoAyuda.add_command(label="Acerca de...")

#Añadimos opciones al menú desplegable Archivo

#barramenu.add_cascade(label="Archivo", menu=archivoMenu)
#sirve para añadir un menú desplegable a la barra de menú principal
#label es el texto que aparecerá en la barra de menú principal

barraMenu.add_cascade(label="Archivo", menu=archivoMenu)

barraMenu.add_cascade(label="Editar", menu=archivoEditar)

barraMenu.add_cascade(label="Herramientas", menu=archivoHerramientas)

barraMenu.add_cascade(label="Ayuda", menu=archivoAyuda)

raiz.mainloop()