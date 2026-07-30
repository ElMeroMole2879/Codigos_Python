# No importa si no se guarda a cada rato con el with podemos guardarlo todo en agenda y al final hacer wb para escribirlo todo al final

import pickle

# CLASE DONDE SE ABRE AGENDA, EL ARCHIVO Y SE GUARDA INFORMACION
class Agenda():
    def __init__(self):
        # SE CREA LA LISTA
        self.agenda = []
        try:
            # ABRIMOS ARCHIVO
            with open("Archivo_Agenda", "rb") as lista_agenda:

                # PUNTERO EN 0
                lista_agenda.seek(0) 

                # PICKLE.LOAD A QUE ARCHIVO SE AGREGARA
                self.agenda = pickle.load(lista_agenda) 
                print(f"\nSe cargaron {len(self.agenda)} contactos en la agenda")
        # EOFError Cuando se intenta leer mas del archivo salta el error
        except (EOFError, FileNotFoundError):
            print("El archivo esta vacio, o no existe se creara un archivo")

    def Menu(self):
        while True:
            try:
                print("-------Bienvenido al Menu---------")
                print("\nIngrese una opcion")
                print("\n1.-Agregar Contactos\n2.-Mostrar Contactos\n3.-Buscar Contactos\n4.-Eliminar Contacto\n5.-Salir")
                opcion = int(input("\nOpcion: "))

                if opcion == 1:
                    self.agregar_contactos()
                    continue
                elif opcion == 2:
                    self.mostrar_contactos()
                    continue
                elif opcion == 3:
                    self.buscar_contactos()
                    continue
                elif opcion == 4:
                    self.eliminar_contacto()
                    continue
                elif opcion == 5:
                    print("\n---------Gracias por usar el programa-----------")
                    break;
                else:
                    print("\nIngrese una opcion valida")
                    continue
            except EOFError:
                print("\nFin del archivo")
    
    def agregar_contactos(self):
        while True:
            try:
                print("-------Agregar Contacto------")
                nombre = input("\nIngrese el nombre del contacto: ").strip().upper()
                telefono_str = input("\nIngrese el telefono del contacto: ").strip()
                correo = input("\nIngrese el correo del contacto: ").strip()

                # convertimos telefono en string para usar .isdigit 
                # si los digitos del telefono son 10 y telefono es digito se entra a la variable
                if len(str(telefono_str)) == 10 and telefono_str.isdigit():

                    # volvemos a convertir telefono a entero
                    telefono = int(telefono_str)

                    # .count("@") para contar cuantas veces aparece ese caracter en el texto
                    # .find(".") para saber en que lugar se encuentra ese caracter
                    # si el correo tiene un arroba y el punto no se encuentra al inicio y al final se entra a la condicion
                    if correo.count("@") == 1 and correo.find(".") > 0 and correo.find(".") < len(correo) - 1:

                        #agregamos los datos que introducimos a la lista de agenda
                        self.agenda.append((nombre, telefono, correo))

                        # abrimos con with para el nombre del archivo y como lo abriremos
                        # y con as es en que variable lo guardaremos
                        with open("Archivo_Agenda", "wb") as lista_agenda:

                            #pickle.dump (lo que guardaremos, en donde lo guardaremos)
                            pickle.dump(self.agenda, lista_agenda)

                            print("\nContacto guardado con exito")
                            break;
                    else:
                        print("\nIngrese un correo valido")
                        continue
                else:
                    print("\nIngresa un numero de telefono valido")
                    continue

            # EOFError no se usa en este caso ya que no estamos leyendo archivo
            except ValueError:
                print("\nValor no valido")

    def mostrar_contactos(self):

        print("-------Contactos en Agenda-------")
        # por cada contacto en agenda se repite el ciclo
        for contacto in self.agenda:

            # con los [] accedemos al lugar de contacto y los mostramos en pantalla con su respectivo dato
            print(f"Nombre: {contacto[0]}, Teléfono: {contacto[1]}, Correo: {contacto[2]}")

    def buscar_contactos(self):

        # pedimos nombre y lo convertimos a .strip().upper
        nombre = input("\nIngrese el nombre: ").strip().upper()

        # encontrados es igual a buscar contacto por contacto en la agenda si el espacio de nombres es igual al nombre asignado
        encontrados = [contacto for contacto in self.agenda if contacto[0] == nombre]

        # si se encontro entra en el if
        if encontrados:
            print(f"\nSe encontró {len(encontrados)} contacto(s):")

            # contacto encontrados por contacto encontrados se imprimen
            for contacto in encontrados:
                print(f"Teléfono: {contacto[1]}, Correo: {contacto[2]}")
        else:
            print(f"\nEl contacto {nombre} no está en la agenda.")

    def eliminar_contacto(self):

        # llamamos a la funcion mostrar contactos para mostrar todos los contactos
        self.mostrar_contactos()
        nombre = input("\nIngrese el nombre del contacto que quiere eliminar: ").strip().upper()
    
        # Buscar coincidencias, if contacto[0] hace que solo se busquen los nombres ya que estan en el lugar 0 de la matriz
        coincidencias = [contacto for contacto in self.agenda if contacto[0] == nombre]

        # If not es una manera de decir coincidencias == False
        if not coincidencias:
            print(f"\nEl contacto {nombre} no se encuentra en la agenda.")
            # return te decuelve a donde se llamo la funcion
            return

        elif len(coincidencias) == 1:
            # Eliminar directamente
            self.agenda.remove(coincidencias[0])
            print(f"\nContacto {nombre} eliminado correctamente.")

        else:
            print(f"\nSe encontraron varios contactos con el nombre {nombre}.")
            # i = 0, enumerate(coincidencias) = te enumera los datos 
            for i, contacto in enumerate(coincidencias):
                # i + 1 = para enumerar
                print(f"{i + 1}. Teléfono: {contacto[1]}, Correo: {contacto[2]}")

        try:
            seleccion = int(input("\nSeleccione el número del contacto a eliminar: "))
            # si seleccion es mayor o igual a 1 y menor o igual al numero de coincidencias
            if 1 <= seleccion <= len(coincidencias):
                # remove() quita el dato que le pases y coincidencias[] metes ahi seleccion - 1 para borrar
                self.agenda.remove(coincidencias[seleccion - 1])
                print("\nContacto eliminado correctamente.")
            else:
                print("\nSelección inválida.")
        except ValueError:
            print("\nEntrada inválida.")

        # Guardar la agenda actualizada
        # wb borra todo lo del archivo pero no importa ya que ya borramos el nombre pero todo lo demas sigue ahi
        with open("Archivo_Agenda", "wb") as lista_agenda:
            pickle.dump(self.agenda, lista_agenda)

MiAgenda = Agenda()
MiAgenda.Menu()