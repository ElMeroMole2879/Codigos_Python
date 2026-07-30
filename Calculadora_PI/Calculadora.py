from tkinter import *

raiz = Tk()

miFrame = Frame(raiz)

miFrame.pack()

Operacion = ""

Resultado = 0

#--------------PANTALLA----------------

NumeroPantalla = StringVar()

pantalla = Entry(miFrame, textvariable=NumeroPantalla)
pantalla.grid(row=1, column=1, padx=10,pady=10, columnspan=4)
pantalla.config(bg="black", fg="green", justify="right")

#--------------PULSACIONES PANTALLA----------------

def NumeroPulsado(num):

    global Operacion


    # Resultado sirve para almacenar el resultado de las operaciones
    #cada vez que se pulsa un numero, se suma al resultado
    # asi podemos ir acumulando el resultado de las operaciones

    if Operacion != "":
        NumeroPantalla.set(num)
        Operacion = ""
    else:
        NumeroPantalla.set(NumeroPantalla.get() + num)

    # IF sirve para saber si se ha pulsado una operacion
    # Si se ha pulsado una operacion, se limpia la pantalla
    # Si no, se va concatenando el numero pulsado
    # Asi podemos escribir numeros de mas de una cifra

    # GET sirve para obtener el valor que tiene la pantalla
    # SET sirve para establecer el valor que tiene la pantalla

#--------------FUNCION SUMA---------------------

def suma(num):

    global Operacion

    global Resultado

    Resultado = float(num)

    Operacion = "suma"

    NumeroPantalla.set("") 

    # NumeroPantalla sirve para actualizar la pantalla
    # cada vez que se pulsa un numero, se actualiza la pantalla

    #Global sirve para indicar que la variable Operacion es global
    #y no local de la funcion suma

#--------------FUNCION RESTA---------------------

def resta(num):

    global Operacion

    global Resultado

    Resultado = float(num)

    Operacion = "resta"

    NumeroPantalla.set("")

#--------------FUNCION MULTIPLICACION---------------------

def multiplicacion(num):

    global Operacion

    global Resultado

    Resultado = float(num)

    Operacion = "multiplicacion"

    NumeroPantalla.set("")

#--------------FUNCION DIVISION---------------------

def division(num):

    global Operacion

    global Resultado

    Resultado = float(num)

    Operacion = "division"

    NumeroPantalla.set("")

#--------------FUNCION EL_RESULTADO---------------------

def el_resultado():

    global Operacion

    global Resultado

    num2 = NumeroPantalla.get()

    try:
        num2 = float(NumeroPantalla.get())
    except:
        NumeroPantalla.set("Error")
        Resultado = 0
        Operacion = ""
        return

    if Operacion == "suma":
        
        Resultado += num2

    elif Operacion == "resta":

        Resultado -= num2
    elif Operacion == "multiplicacion":

        Resultado *= num2

    elif Operacion == "division":

        if float(num2) == 0:   
            Resultado /= float(num2)

            Resultado = 0

            Operacion = ""

            return
        else:

            Resultado /= float(num2)

    NumeroPantalla.set(Resultado)

    Resultado = 0

    Operacion = ""

    # IF sirve para saber que operacion se ha pulsado
    # y realizar la operacion correspondiente

    #Cada vez que se pulsa el boton igual, se realiza la operacion
    # y se muestra el resultado en la pantalla
    #Despues se reinicia el resultado a 0 para poder realizar nuevas operaciones

#--------------FILA 1---------------------

boton7 = Button(miFrame, text="7", width=3, command=lambda: NumeroPulsado("7"))
boton7.grid(row=2, column=1)

boton8 = Button(miFrame, text="8", width=3, command=lambda: NumeroPulsado("8"))
boton8.grid(row=2, column=2)

boton9 = Button(miFrame, text="9", width=3, command=lambda: NumeroPulsado("9"))
boton9.grid(row=2, column=3)

botonDiv = Button(miFrame, text="/", width=3, command=lambda: division(NumeroPantalla.get()))
botonDiv.grid(row=2, column=4)

#--------------FILA 2---------------------

#LAMBDA nos permite pasar parametros a la funcion dentro de un boton
#sin necesidad de crear una funcion aparte
#en este caso, pasamos el numero pulsado a la funcion NumeroPulsado
#asi podemos reutilizar la misma funcion para todos los botones numericos

boton4 = Button(miFrame, text="4", width=3, command=lambda: NumeroPulsado("4"))
boton4.grid(row=3, column=1)

boton5 = Button(miFrame, text="5", width=3, command=lambda: NumeroPulsado("5"))
boton5.grid(row=3, column=2)

boton6 = Button(miFrame, text="6", width=3, command=lambda: NumeroPulsado("6"))
boton6.grid(row=3, column=3)

botonMult = Button(miFrame, text="*", width=3, command=lambda: multiplicacion(NumeroPantalla.get()))
botonMult.grid(row=3, column=4)

#--------------FILA 3---------------------

boton1 = Button(miFrame, text="1", width=3, command=lambda: NumeroPulsado("1"))
boton1.grid(row=4, column=1)

boton2 = Button(miFrame, text="2", width=3, command=lambda: NumeroPulsado("2"))
boton2.grid(row=4, column=2)

boton3 = Button(miFrame, text="3", width=3, command=lambda: NumeroPulsado("3"))
boton3.grid(row=4, column=3)

botonRest = Button(miFrame, text="-", width=3, command=lambda: resta(NumeroPantalla.get()))
botonRest.grid(row=4, column=4)

#--------------FILA 4---------------------

boton0 = Button(miFrame, text="0", width=3, command=lambda: NumeroPulsado("0"))
boton0.grid(row=5, column=1)

botonPunto = Button(miFrame, text=".", width=3, command=lambda: NumeroPulsado("."))
botonPunto.grid(row=5, column=2)

botonIgual = Button(miFrame, text="=", width=3, command = lambda: el_resultado())
botonIgual.grid(row=5, column=3)

botonSuma = Button(miFrame, text="+", width=3, command=lambda: suma(NumeroPantalla.get()))
botonSuma.grid(row=5, column=4)
raiz.mainloop()