class Calculadora:
    def __init__(self, calificacion1, calificacion2, calificacion3, promedio):
        self.calificacion1 = calificacion1
        self.calificacion2 = calificacion2
        self.calificacion3 = calificacion3
        self.promedio = promedio

    def pedir_calificaciones(self):
        while True:
            try:
                self.calificacion1 = float(input("Ingrese la primera calificación: "))
                self.calificacion2 = float(input("Ingrese la segunda calificación: "))
                self.calificacion3 = float(input("Ingrese la tercera calificación: "))
                break
            except ValueError:
                print("Por favor, ingrese un número válido.")

    def calcular_promedio(self):
        self.promedio = (self.calificacion1 + self.calificacion2 + self.calificacion3) / 3
        return self.promedio

calculadora = Calculadora(0, 0, 0, 0)
calculadora.pedir_calificaciones()
promedio = calculadora.calcular_promedio()
print(f"El promedio es: {promedio}")