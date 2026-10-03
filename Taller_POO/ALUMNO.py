class Promedio:
    def __init__(self):
        self.calificaciones = []
        self.promedio = 0.0

    def pedir_calificaciones(self):
        while True:
            try:
                calificacion = float(input("Ingrese una calificación (o escriba 'fin' para terminar): "))
                if 0 <= calificacion <= 100:
                    self.calificaciones.append(calificacion)
                else:
                    print("Error: La calificación debe estar entre 0 y 100.")
            except ValueError:
                if input("¿Desea terminar de ingresar calificaciones? (s/n): ").lower() == 's':
                    break
                else:
                    print("Por favor, ingrese un número válido.")

    def calcular_promedio(self):
        if len(self.calificaciones) == 0:
            print("No se han ingresado calificaciones.")
            return
        self.promedio = sum(self.calificaciones) / len(self.calificaciones)

        if self.promedio >= 70:
            print(f"El alumno ha aprobado con un promedio de {self.promedio:.2f}.")
        else:
            print(f"El alumno ha reprobado con un promedio de {self.promedio:.2f}.")

Promedio = Promedio()
Promedio.pedir_calificaciones()
Promedio.calcular_promedio()