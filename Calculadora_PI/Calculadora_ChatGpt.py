from tkinter import *

raiz = Tk()

miFrame = Frame(raiz)
miFrame.pack()

Operacion = ""
Resultado = 0
NuevaOperacion = True

#--------------PANTALLA----------------

NumeroPantalla = StringVar()

pantalla = Entry(miFrame, textvariable=NumeroPantalla)
pantalla.grid(row=1, column=1, padx=10,pady=10, columnspan=4)
pantalla.config(bg="black", fg="green", justify="right")

#--------------PULSACIONES PANTALLA----------------

def NumeroPulsado(num):
    global Operacion, NuevaOperacion

    if NuevaOperacion:
        NumeroPantalla.set(num)
        NuevaOperacion = False
    else:
        NumeroPantalla.set(NumeroPantalla.get() + num)

#--------------OPERACIONES---------------------

def prepara_operacion(op, num):
    global Operacion, Resultado, NuevaOperacion

    try:
        Resultado = float(num)
    except:
        NumeroPantalla.set("Error")
        Resultado = 0
        return

    Operacion = op
    NuevaOperacion = True


def suma(num):
    prepara_operacion("suma", num)

def resta(num):
    prepara_operacion("resta", num)

def multiplicacion(num):
    prepara_operacion("multiplicacion", num)

def division(num):
    prepara_operacion("division", num)

#--------------FUNCION EL_RESULTADO---------------------

def el_resultado():
    global Operacion, Resultado, NuevaOperacion

    try:
        num2 = float(NumeroPantalla.get())
    except:
        NumeroPantalla.set("Error")
        Operacion = ""
        return

    if Operacion == "suma":
        Resultado += num2

    elif Operacion == "resta":
        Resultado -= num2

    elif Operacion == "multiplicacion":
        Resultado *= num2

    elif Operacion == "division":
        if num2 == 0:
            NumeroPantalla.set("Error")
            Operacion = ""
            return
        Resultado /= num2

    NumeroPantalla.set(Resultado)
    Operacion = ""
    NuevaOperacion = True

#--------------FILA 1---------------------

Button(miFrame, text="7", width=3, command=lambda: NumeroPulsado("7")).grid(row=2, column=1)
Button(miFrame, text="8", width=3, command=lambda: NumeroPulsado("8")).grid(row=2, column=2)
Button(miFrame, text="9", width=3, command=lambda: NumeroPulsado("9")).grid(row=2, column=3)
Button(miFrame, text="/", width=3, command=lambda: division(NumeroPantalla.get())).grid(row=2, column=4)

#--------------FILA 2---------------------

Button(miFrame, text="4", width=3, command=lambda: NumeroPulsado("4")).grid(row=3, column=1)
Button(miFrame, text="5", width=3, command=lambda: NumeroPulsado("5")).grid(row=3, column=2)
Button(miFrame, text="6", width=3, command=lambda: NumeroPulsado("6")).grid(row=3, column=3)
Button(miFrame, text="*", width=3, command=lambda: multiplicacion(NumeroPantalla.get())).grid(row=3, column=4)

#--------------FILA 3---------------------

Button(miFrame, text="1", width=3, command=lambda: NumeroPulsado("1")).grid(row=4, column=1)
Button(miFrame, text="2", width=3, command=lambda: NumeroPulsado("2")).grid(row=4, column=2)
Button(miFrame, text="3", width=3, command=lambda: NumeroPulsado("3")).grid(row=4, column=3)
Button(miFrame, text="-", width=3, command=lambda: resta(NumeroPantalla.get())).grid(row=4, column=4)

#--------------FILA 4---------------------

Button(miFrame, text="0", width=3, command=lambda: NumeroPulsado("0")).grid(row=5, column=1)
Button(miFrame, text=".", width=3, command=lambda: NumeroPulsado(".")).grid(row=5, column=2)
Button(miFrame, text="=", width=3, command=el_resultado).grid(row=5, column=3)
Button(miFrame, text="+", width=3, command=lambda: suma(NumeroPantalla.get())).grid(row=5, column=4)

raiz.mainloop()