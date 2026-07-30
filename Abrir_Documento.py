from tkinter import *
from tkinter import filedialog

raiz = Tk()

def abrir():

    fichero = filedialog.askopenfilename(title="Abrir documento", initialdir="C:/",
                                         filetypes=(("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")))
    
    # filedialog.askopenfilename() devuelve la ruta del archivo seleccionado por el usuario
    #initialdir es el directorio inicial que se muestra al abrir el cuadro de diálogo
    #filetypes es una tupla que especifica los tipos de archivos que se pueden seleccionar en el cuadro de diálogo
    
    print(fichero)

Button(raiz, text="Abrir documento", command=abrir).pack()

raiz.mainloop()