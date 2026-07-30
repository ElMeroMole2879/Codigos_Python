from tkinter import *

raiz = Tk()

varOpcion = IntVar()

#Etiqueta para el grupo de Radiobuttons

#Función para imprimir la opción seleccionada
#varOpcion.get() devuelve el valor del Radiobutton seleccionado

def imprimirSeleccion():
    #print("Opción seleccionada:", varOpcion.get())
    if varOpcion.get() == 1:
        etiquetaResultado.config(text="Has seleccionado la Opción 1")
    else:
        etiquetaResultado.config(text="Has seleccionado la Opción 2")

Label(raiz, text="Selecciona una opción:").pack()

#Value debe ser único para cada Radiobutton dentro del mismo grupo
#Si se selecciona este botón, varOpcion tomará el valor 1

Radiobutton(raiz, text="Opción 1", variable=varOpcion, value=1, command=imprimirSeleccion).pack()

#Si se selecciona este botón, varOpcion tomará el valor 2

Radiobutton(raiz, text="Opción 2", variable=varOpcion, value=2, command=imprimirSeleccion).pack()

etiquetaResultado = Label(raiz)
etiquetaResultado.pack()

raiz.mainloop()