sitio_web = "www.axelprueba.com"

# SLICING DE CADENAS 0 = INICIO, 1 = FIN, 2 = SALTO
subcadena = sitio_web[0:3]

subcadena2 = sitio_web[4:14:1]
print(subcadena)
print(subcadena2)

#SOLO IMPRIME LOS NUMEROS PARES DE LA CADENA
numeros = "0123456789"
print(numeros[0:10:2])

subcadena3 = sitio_web[0:-4:1]
print(subcadena3)

colores =["rojo", "verde", "azul", "amarillo", "naranja", "morado"]

print(colores[0:-3:1])