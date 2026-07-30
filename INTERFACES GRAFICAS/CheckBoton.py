from tkinter import *
from turtle import title

raiz = Tk()

raiz.title("Ejemplo de Checkbuttons")

OpcionA = IntVar()
OpcionB = IntVar() 
OpcionC = IntVar()

def mostrarSeleccion():
    seleccion = "Has seleccionado:\n"
    if OpcionA.get() == 1:
        seleccion += "Opción A\n"
    if OpcionB.get() == 1:
        seleccion += "Opción B\n"
    if OpcionC.get() == 1:
        seleccion += "Opción C\n"
    TextoResultado.config(text=seleccion)

#PhotonImage para cargar una imagen desde un archivo
#imagen = PhotoImage(file="ruta/a/tu/imagen.png")
#Label(raiz, image=imagen).pack()

frame = Frame(raiz)
frame.pack()

Label(frame, text="Selecciona las opciones que desees:").pack()

#SI DESEAMOS QUE LOS CHECK BUTTONS SEAN DE ALGUNA IMAGEN CON FRAME O LABEL
# SI NO QUEREMOS PUES LE PONEMOS DE RAIZ DIRECTO

#Onvalue y Offvalue definen los valores que tomará la variable asociada
#cuando el Checkbutton esté seleccionado o no seleccionado respectivamente

Checkbutton(frame, text="Opción A", variable=OpcionA, onvalue=1, offvalue=0, command=mostrarSeleccion).pack()
Checkbutton(frame, text="Opción B", variable=OpcionB, onvalue=1, offvalue=0, command=mostrarSeleccion).pack()
Checkbutton(frame, text="Opción C", variable=OpcionC, onvalue=1, offvalue=0, command=mostrarSeleccion).pack()

TextoResultado = Label(raiz)
TextoResultado.pack()

raiz.mainloop()