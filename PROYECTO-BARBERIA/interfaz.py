"""
Interfaz gráfica (Tkinter) del sistema de la barbería — adaptada al backend con
login, empleados, inventario y finanzas.

Archivos que deben estar junto a este, en la misma carpeta:
   config.py, inicializar_bd.py, main.py, y la carpeta bd/ completa

Antes de la primera vez:
   python inicializar_bd.py
   (OJO: ese script BORRA la base de datos si ya existía y la vuelve a crear vacía,
   con el usuario admin/12345. Solo se ejecuta UNA vez, a mano. Esta interfaz nunca
   lo llama sola, para no borrar tu información sin querer.)

Requisito:  pip install mysql-connector-python
Ejecutar:   python interfaz.py
"""
import ctypes
import os
import tkinter as tk
import tkinter.font as tkfont
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from tkinter import filedialog, messagebox, ttk

import mysql.connector

from bd.citas import Cita
from bd.cliente import Cliente
from bd.conexion import ConexionDB
from bd.empleados import Empleado
from bd.entradas_inventario import EntradaInventario
from bd.finanzas import Finanzas
from bd.generador_respaldos import GestorRespaldos
from bd.historial import HistorialCliente, HistorialEmpleado
from bd.nomina import Nomina
from bd.notas import Nota
from bd.producto import Producto
from bd.reportes import Reporte
from bd.servicios import Servicio
from bd.usuario import Usuario
from bd.venta import Venta

# ----------------------------------------------------------------------
# Independizar icono en la barra de tareas de Windows
# ----------------------------------------------------------------------
try:
    app_id = 'mi_barberia.sistema_gestion.1_0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
except Exception:
    pass

# ----------------------------------------------------------------------
# Apariencia
# ----------------------------------------------------------------------
TINTA = "#14213d"
TINTA_CLARA = "#223a66"
ROJO = "#c1272d"
ROJO_CLARO = "#e0454d"
ROJO_OSCURO = "#9f1d22"
AZUL_POSTE = "#2a4d8f"
AZUL_POSTE_CLARO = "#3f67b8"
FONDO = "#eef1f5"
SUPERFICIE = "#ffffff"
FILA_ALTERNA = "#f3f5f9"
LINEA = "#cfd6e0"
TEXTO = "#1b2333"
TEXTO_SUAVE = "#5b6577"

FUENTE = ("Segoe UI", 10)
FUENTE_NEGRITA = ("Segoe UI", 10, "bold")
FUENTE_TITULO = ("Georgia", 20, "bold")
FUENTE_SUBTITULO = ("Georgia", 13, "bold")
FUENTE_TOTAL = ("Georgia", 20, "bold")

ESTADOS_CITA = ["Pendiente", "Completada", "Cancelada"]
METODOS_PAGO = ["Efectivo", "Tarjeta", "Transferencia"]


class ErrorOperacion(Exception):
    """
    Se levanta cuando un método del backend regresa False/None sin dar más detalle.
    El backend imprime la causa exacta en la terminal (con print), pero no la regresa
    como texto, así que aquí solo podemos dar un mensaje general y apuntar a la terminal.
    """


# ----------------------------------------------------------------------
# Utilidades generales
# ----------------------------------------------------------------------

class EntradaValidada(ttk.Entry):
    """
    Caja de texto personalizada que bloquea el teclado según el tipo de dato.
    Tipos soportados: 'texto' (por defecto), 'entero' (solo números), 'decimal' (números y un punto),
    'letras' (solo letras y espacios, sin números).
    """
    def __init__(self, padre, tipo="texto", **kwargs):
        super().__init__(padre, **kwargs)
        if tipo == "entero":
            vcmd = (self.register(self._validar_entero), '%P')
            self.configure(validate="key", validatecommand=vcmd)
        elif tipo == "decimal":
            vcmd = (self.register(self._validar_decimal), '%P')
            self.configure(validate="key", validatecommand=vcmd)
        elif tipo == "letras":
            vcmd = (self.register(self._validar_letras), '%P')
            self.configure(validate="key", validatecommand=vcmd)

    def _validar_entero(self, P):
        return P == "" or P.isdigit()

    def _validar_decimal(self, P):
        if P == "":
            return True
        if P.count('.') > 1:
            return False
        return P.replace('.', '').isdigit()

    def _validar_letras(self, P):
        if P == "":
            return True
        # Acepta letras (incluyendo acentos, ñ) y espacios. Bloquea números y símbolos.
        return all(c.isalpha() or c.isspace() for c in P)


def dinero(valor):
    return f"${Decimal(valor or 0):,.2f}"


def hoy():
    return date.today().strftime("%Y-%m-%d")


def con_errores(funcion):
    def envoltura(*args, **kwargs):
        try:
            return funcion(*args, **kwargs)
        except ErrorOperacion as e:
            messagebox.showerror(
                "No se pudo completar la operación",
                f"{e}\n\nRevisa la terminal: ahí el backend imprime la causa exacta.",
            )
        except ValueError as e:
            messagebox.showwarning("Revisa los datos", str(e))
        except mysql.connector.Error as e:
            messagebox.showerror("Error de base de datos", str(e))
        except OSError as e:
            messagebox.showerror("Error de archivo", str(e))
    envoltura.__name__ = funcion.__name__
    return envoltura


def convertir(valor, tipo, etiqueta, obligatorio=True, largo_maximo=None, defecto="0"):
    valor = str(valor).strip() if valor is not None else ""
    if not valor:
        if obligatorio:
            raise ValueError(f"El campo '{etiqueta}' es obligatorio.")
        valor = defecto if tipo in ("decimal", "porcentaje", "entero") else ""
        if not valor:
            return None

    if tipo == "texto":
        if largo_maximo and len(valor) > largo_maximo:
            raise ValueError(f"'{etiqueta}' admite máximo {largo_maximo} caracteres.")
        return valor

    if tipo == "entero":
        if not (valor.isascii() and valor.isdigit()) or int(valor) > 2_000_000_000:
            raise ValueError(f"'{etiqueta}' debe ser un número entero (0 o mayor).")
        return int(valor)

    try:
        numero = Decimal(valor.replace(",", ""))
    except InvalidOperation:
        raise ValueError(f"'{etiqueta}' debe ser un número, por ejemplo 150 o 150.50.")
    if not numero.is_finite() or numero < 0 or numero >= 10 ** 8:
        raise ValueError(f"'{etiqueta}' debe ser un número positivo y razonable.")
    if tipo == "porcentaje" and numero > 100:
        raise ValueError(f"'{etiqueta}' debe estar entre 0 y 100.")
    return numero.quantize(Decimal("0.01"))


def validar_fecha(texto, etiqueta="La fecha", obligatorio=True):
    texto = texto.strip()
    if not texto:
        if obligatorio:
            raise ValueError(f"{etiqueta} es obligatoria, formato AAAA-MM-DD.")
        return None
    try:
        return datetime.strptime(texto, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"{etiqueta} debe tener el formato AAAA-MM-DD, por ejemplo {hoy()}.")


def validar_hora(texto):
    try:
        return datetime.strptime(texto.strip(), "%H:%M").time()
    except ValueError:
        raise ValueError("La hora debe tener el formato HH:MM, por ejemplo 15:30.")


def formatear_hora(valor):
    if isinstance(valor, timedelta):
        total = int(valor.total_seconds())
        h, resto = divmod(total, 3600)
        m, s = divmod(resto, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"
    return str(valor)


def nombre_completo(fila, prefijo=""):
    partes = [fila.get(f"{prefijo}nombres") or fila.get("nombres"),
              fila.get(f"{prefijo}primer_apellido") or fila.get("primer_apellido"),
              fila.get(f"{prefijo}segundo_apellido") or fila.get("segundo_apellido")]
    return " ".join(p for p in partes if p)


def crear_tabla(padre, columnas, altura=8):
    contenedor = ttk.Frame(padre)
    claves = [c[0] for c in columnas]
    tabla = ttk.Treeview(
        contenedor, columns=claves, show="headings", height=altura,
        selectmode="browse", displaycolumns=claves[1:],
    )
    for clave, encabezado, ancho, ancla in columnas:
        tabla.heading(clave, text=encabezado, anchor=ancla)
        tabla.column(clave, width=ancho, anchor=ancla)
    barra = ttk.Scrollbar(contenedor, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=barra.set)
    tabla.pack(side="left", fill="both", expand=True)
    barra.pack(side="right", fill="y")
    tabla.tag_configure("par", background=SUPERFICIE)
    tabla.tag_configure("impar", background=FILA_ALTERNA)
    return contenedor, tabla


def llenar_tabla(tabla, filas, claves, formatos=None, etiqueta=None):
    tabla.delete(*tabla.get_children())
    por_id = {}
    for i, fila in enumerate(filas):
        valores = []
        for j, clave in enumerate(claves):
            v = fila.get(clave)
            formato = formatos[j] if formatos and j < len(formatos) else None
            valores.append("" if v is None else (formato(v) if formato else str(v)))
        iid = str(fila.get(claves[0]))
        etiquetas = ["par" if i % 2 == 0 else "impar"]
        if etiqueta:
            etiquetas.append(etiqueta(fila))
        tabla.insert("", "end", iid=iid, values=valores, tags=etiquetas)
        por_id[iid] = fila
    return por_id


def seleccionado(tabla, mensaje):
    seleccion = tabla.selection()
    if not seleccion:
        messagebox.showinfo("Falta una selección", mensaje)
        return None
    return seleccion[0]


class ComboConIds(ttk.Combobox):
    def __init__(self, padre, **opciones):
        super().__init__(padre, state="readonly", **opciones)
        self._ids = {}

    def cargar(self, opciones):
        anterior = self.get()
        self._ids = {}
        for id_, texto in opciones:
            if texto in self._ids:
                texto = f"{texto} (#{id_})"
            self._ids[texto] = id_
        self["values"] = list(self._ids)
        self.set(anterior if anterior in self._ids else "")

    def valor(self):
        return self._ids.get(self.get())


class BandaBarbero(tk.Canvas):
    COLORES = [ROJO, SUPERFICIE, AZUL_POSTE]

    def __init__(self, padre, alto=8):
        super().__init__(padre, height=alto, highlightthickness=0, bg=SUPERFICIE)
        self.alto = alto
        self.bind("<Configure>", self.dibujar)

    def dibujar(self, _evento=None):
        self.delete("all")
        paso = 14
        x, i = -self.alto, 0
        while x < self.winfo_width():
            self.create_polygon(
                x, self.alto, x + paso, self.alto, x + paso + self.alto, 0, x + self.alto, 0,
                fill=self.COLORES[i % 3], outline="",
            )
            x += paso
            i += 1


def interpolar_color(color_izq, color_der, factor):
    color_izq, color_der = color_izq.lstrip("#"), color_der.lstrip("#")
    r1, g1, b1 = int(color_izq[0:2], 16), int(color_izq[2:4], 16), int(color_izq[4:6], 16)
    r2, g2, b2 = int(color_der[0:2], 16), int(color_der[2:4], 16), int(color_der[4:6], 16)
    r = round(r1 + (r2 - r1) * factor)
    g = round(g1 + (g2 - g1) * factor)
    b = round(b1 + (b2 - b1) * factor)
    return f"#{r:02x}{g:02x}{b:02x}"


class EncabezadoDegradado(tk.Canvas):
    def __init__(self, padre, titulo, subtitulo, color_izq=TINTA, color_der=AZUL_POSTE, alto=58):
        super().__init__(padre, height=alto, highlightthickness=0, bd=0, bg=FONDO)
        self.titulo = titulo
        self.subtitulo = subtitulo
        self.color_izq = color_izq
        self.color_der = color_der
        self.alto = alto
        self.bind("<Configure>", self._dibujar)

    def _dibujar(self, _evento=None):
        self.delete("all")
        ancho = self.winfo_width()
        if ancho <= 1:
            return
        for x in range(ancho):
            self.create_line(x, 0, x, self.alto, fill=interpolar_color(self.color_izq, self.color_der, x / max(ancho - 1, 1)))
        self.create_text(22, self.alto / 2, text=self.titulo, font=FUENTE_TITULO, fill="white", anchor="w")
        self.create_text(ancho - 22, self.alto / 2, text=self.subtitulo, font=("Segoe UI", 9), fill="#dfe7f5", anchor="e")


class BotonDegradado(tk.Canvas):
    def __init__(self, padre, text, command=None, color_izq=ROJO_CLARO, color_der=ROJO_OSCURO,
                 color_hover_izq=None, color_hover_der=None, fg="white", relleno_horizontal=22, alto=34):
        super().__init__(padre, height=alto, highlightthickness=0, bd=0, bg=FONDO, cursor="hand2")
        self.texto = text
        self.command = command
        self.color_izq = color_izq
        self.color_der = color_der
        self.color_hover_izq = color_hover_izq or ROJO
        self.color_hover_der = color_hover_der or color_der
        self.fg = fg
        self.alto = alto
        self._hover = False

        ancho_texto = tkfont.Font(font=FUENTE_NEGRITA).measure(text)
        self.ancho = ancho_texto + relleno_horizontal * 2
        self.configure(width=self.ancho)

        self.bind("<Configure>", self._dibujar)
        self.bind("<Enter>", self._al_entrar)
        self.bind("<Leave>", self._al_salir)
        self.bind("<Button-1>", self._al_clic)
        self._dibujar()

    def _dibujar(self, _evento=None):
        self.delete("all")
        ancho = self.winfo_width() or self.ancho
        alto = self.winfo_height() or self.alto
        izq, der = (self.color_hover_izq, self.color_hover_der) if self._hover else (self.color_izq, self.color_der)
        for x in range(ancho):
            self.create_line(x, 0, x, alto, fill=interpolar_color(izq, der, x / max(ancho - 1, 1)))
        self.create_text(ancho / 2, alto / 2, text=self.texto, fill=self.fg, font=FUENTE_NEGRITA)

    def _al_entrar(self, _evento=None):
        self._hover = True
        self._dibujar()

    def _al_salir(self, _evento=None):
        self._hover = False
        self._dibujar()

    def _al_clic(self, _evento=None):
        if self.command:
            self.command()


def aplicar_estilos(raiz):
    estilo = ttk.Style(raiz)
    estilo.theme_use("clam")
    estilo.configure(".", font=FUENTE, background=FONDO, foreground=TEXTO, bordercolor=LINEA)
    estilo.configure("TLabelframe", background=FONDO, bordercolor=LINEA)
    estilo.configure("TLabelframe.Label", background=FONDO, foreground=TINTA, font=FUENTE_NEGRITA)
    estilo.configure("TEntry", fieldbackground=SUPERFICIE, padding=4)
    estilo.configure("TCombobox", fieldbackground=SUPERFICIE, background="#dfe5ee", padding=4)
    estilo.map("TCombobox", fieldbackground=[("readonly", SUPERFICIE)],
               selectbackground=[("readonly", SUPERFICIE)], selectforeground=[("readonly", TEXTO)])
    estilo.configure("TSpinbox", fieldbackground=SUPERFICIE, padding=4)

    estilo.configure("TButton", padding=(12, 6), background="#dfe5ee", foreground=TINTA, borderwidth=1)
    estilo.map("TButton", background=[("active", "#cdd6e3")])

    estilo.configure("TNotebook", background=FONDO, borderwidth=0)
    estilo.configure("TNotebook.Tab", padding=(16, 8), background="#dfe5ee", foreground=TEXTO_SUAVE, font=FUENTE_NEGRITA)
    estilo.map("TNotebook.Tab", background=[("selected", FONDO)], foreground=[("selected", ROJO)])

    estilo.configure("Treeview", rowheight=26, background=SUPERFICIE, fieldbackground=SUPERFICIE, bordercolor=LINEA)
    estilo.configure("Treeview.Heading", background=TINTA, foreground="white", font=FUENTE_NEGRITA, padding=(4, 6), relief="flat")
    estilo.map("Treeview.Heading", background=[("active", AZUL_POSTE)])
    estilo.map("Treeview", background=[("selected", AZUL_POSTE)], foreground=[("selected", "white")])

    estilo.configure("Total.TLabel", font=FUENTE_TOTAL, foreground=TINTA)
    estilo.configure("Encabezado.TLabel", font=FUENTE_SUBTITULO, foreground=TINTA, background=FONDO)


# ----------------------------------------------------------------------
# Ventana de inicio de sesión
# ----------------------------------------------------------------------
class VentanaLogin(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Barbería · Iniciar sesión")
        self.geometry("420x340")
        self.resizable(False, False)
        self.configure(bg=FONDO)
        aplicar_estilos(self)
        self.usuario_autenticado = None

        # Carga del logo personalizado
        try:
            ruta_ico = os.path.join(os.path.dirname(__file__), "logo.ico")
            if os.path.exists(ruta_ico):
                self.iconbitmap(ruta_ico)
        except Exception:
            pass  # Si hay error cargando la imagen, simplemente se usa el predeterminado de Tkinter

        tk.Label(self, text="Barbería", font=FUENTE_TITULO, bg=FONDO, fg=TINTA).pack(pady=(34, 0))
        BandaBarbero(self).pack(fill="x", pady=(10, 24), padx=40)

        caja = ttk.Frame(self)
        caja.pack(padx=40, fill="x")

        self.var_usuario = tk.StringVar()
        self.var_password = tk.StringVar()

        ttk.Label(caja, text="Usuario").pack(anchor="w")
        entrada_usuario = ttk.Entry(caja, textvariable=self.var_usuario)
        entrada_usuario.pack(fill="x", pady=(2, 14))
        ttk.Label(caja, text="Contraseña").pack(anchor="w")
        entrada_password = ttk.Entry(caja, textvariable=self.var_password, show="*")
        entrada_password.pack(fill="x", pady=(2, 20))

        BotonDegradado(caja, text="Iniciar sesión", command=self.entrar).pack(fill="x")

        entrada_usuario.bind("<Return>", lambda _e: entrada_password.focus())
        entrada_password.bind("<Return>", lambda _e: self.entrar())
        entrada_usuario.focus()

    def entrar(self):
        usuario = self.var_usuario.get().strip()
        password = self.var_password.get()
        if not usuario or not password:
            messagebox.showwarning("Faltan datos", "Escribe tu usuario y tu contraseña.")
            return
        try:
            resultado = Usuario.validar_login(usuario, password)
        except mysql.connector.Error as e:
            messagebox.showerror(
                "No se pudo iniciar",
                f"No se pudo conectar con MySQL.\nRevisa que el servidor esté encendido y que config.py sea correcto.\n\n{e}",
            )
            return
        if resultado is None:
            messagebox.showwarning("Acceso denegado", "Usuario o contraseña incorrectos.")
        elif resultado == "INACTIVO":
            messagebox.showwarning("Acceso denegado", "Ese usuario existe pero está dado de baja.")
        else:
            self.usuario_autenticado = resultado
            self.destroy()


# ----------------------------------------------------------------------
# Citas
# ----------------------------------------------------------------------
class PanelCitas(ttk.Frame):
    def __init__(self, padre):
        super().__init__(padre, padding=14)
        self.citas_cargadas = []
        self.var_fecha = tk.StringVar(value=hoy())
        self.var_hora = tk.StringVar(value="10:00")
        self.var_filtro = tk.StringVar()

        formulario = ttk.LabelFrame(self, text=" Nueva cita ", padding=12)
        formulario.pack(fill="x")
        self.cb_cliente = ComboConIds(formulario, width=30)
        self.cb_empleado = ComboConIds(formulario, width=30)
        self.cb_servicio = ComboConIds(formulario, width=30)
        self.cb_estado = ttk.Combobox(formulario, values=ESTADOS_CITA, state="readonly", width=30)
        self.cb_estado.set(ESTADOS_CITA[0])
        campos = [
            ("Fecha (AAAA-MM-DD)", ttk.Entry(formulario, textvariable=self.var_fecha, width=32)),
            ("Hora (HH:MM)", ttk.Entry(formulario, textvariable=self.var_hora, width=32)),
            ("Cliente", self.cb_cliente),
            ("Barbero / empleado", self.cb_empleado),
            ("Servicio", self.cb_servicio),
            ("Estado (para cambiarlo luego)", self.cb_estado),
        ]
        for i, (texto, widget) in enumerate(campos):
            fila, columna = divmod(i, 3)
            ttk.Label(formulario, text=texto).grid(row=fila * 2, column=columna, sticky="w", padx=(0, 20))
            widget.grid(row=fila * 2 + 1, column=columna, sticky="w", padx=(0, 20), pady=(0, 8))

        botones = ttk.Frame(formulario)
        botones.grid(row=4, column=0, columnspan=3, sticky="w", pady=(4, 0))
        BotonDegradado(botones, text="Agendar cita", command=self.agendar).pack(side="left")
        ttk.Button(botones, text="Aplicar estado a la cita elegida", command=self.aplicar_estado).pack(side="left", padx=6)
        ttk.Button(botones, text="Eliminar cita por error", command=self.eliminar_por_error).pack(side="left")

        filtro = ttk.Frame(self)
        filtro.pack(fill="x", pady=(14, 6))
        ttk.Label(filtro, text="Mostrar solo la fecha").pack(side="left")
        entrada = ttk.Entry(filtro, textvariable=self.var_filtro, width=14)
        entrada.pack(side="left", padx=8)
        entrada.bind("<Return>", lambda _e: self.pintar_tabla())
        ttk.Button(filtro, text="Filtrar", command=self.pintar_tabla).pack(side="left")
        ttk.Button(filtro, text="Hoy", command=lambda: self._filtrar(hoy())).pack(side="left", padx=6)
        ttk.Button(filtro, text="Ver todas", command=lambda: self._filtrar("")).pack(side="left")
        ttk.Button(filtro, text="Actualizar", command=self.refrescar).pack(side="right")

        contenedor, self.tabla = crear_tabla(self, [
            ("id", "ID", 0, "w"), ("cliente", "Cliente", 220, "w"), ("telefono", "Teléfono", 110, "w"),
            ("empleado", "Barbero", 160, "w"), ("servicio", "Servicio", 160, "w"), ("precio", "Precio", 90, "e"),
            ("fecha", "Fecha", 100, "w"), ("hora", "Hora", 70, "w"), ("estado", "Estado", 100, "w"),
        ], altura=13)
        contenedor.pack(fill="both", expand=True)
        self.tabla.tag_configure("cancelada", foreground="#8b93a1")
        self.tabla.tag_configure("completada", foreground="#1f7a45")

    def _filtrar(self, texto):
        self.var_filtro.set(texto)
        self.pintar_tabla()

    @con_errores
    def refrescar(self):
        self.cb_cliente.cargar([(f["id_cliente"], nombre_completo(f)) for f in Cliente.obtener_todos_los_clientes()])
        self.cb_empleado.cargar([(f["id_empleado"], nombre_completo(f)) for f in Empleado.obtener_empleados_activos()])
        self.cb_servicio.cargar([(f["id_servicio"], f["nombre_servicio"]) for f in Servicio.obtener_todos_los_servicios()])
        self.citas_cargadas = Cita.obtener_todas_las_citas()
        self.pintar_tabla()

    def pintar_tabla(self):
        texto = self.var_filtro.get().strip()
        filas = self.citas_cargadas
        if texto:
            fecha = validar_fecha(texto, "El filtro de fecha").isoformat()
            filas = [f for f in filas if str(f["fecha_cita"]) == fecha]
        for f in filas:
            f["cliente"] = f"{f.get('nombre_cliente', '')} {f.get('apellido_cliente', '')}".strip()
            f["empleado"] = f.get("nombre_barbero", "")
        llenar_tabla(
            self.tabla, filas,
            claves=["id_cita", "cliente", "telefono", "empleado", "nombre_servicio", "precio_actual", "fecha_cita", "hora_cita", "estado"],
            formatos=[None, None, None, None, None, dinero, None, formatear_hora, None],
            etiqueta=lambda f: f["estado"].lower(),
        )

    @con_errores
    def agendar(self):
        fecha = validar_fecha(self.var_fecha.get())
        hora = validar_hora(self.var_hora.get())
        id_cliente, id_empleado, id_servicio = self.cb_cliente.valor(), self.cb_empleado.valor(), self.cb_servicio.valor()
        if None in (id_cliente, id_empleado, id_servicio):
            raise ValueError("Elige el cliente, el barbero y el servicio de la cita.")

        hora_texto = hora.strftime("%H:%M:%S")
        if not Cita.agendar_cita(id_cliente, id_empleado, id_servicio, fecha.isoformat(), hora_texto):
            raise ErrorOperacion("No se pudo agendar la cita (puede que ese barbero ya tenga otra cita a esa hora).")
        self.refrescar()

    @con_errores
    def aplicar_estado(self):
        id_cita = seleccionado(self.tabla, "Elige una cita de la tabla y el estado que quieres aplicarle.")
        if id_cita is None:
            return
        if not Cita.actualizar_estado_cita(int(id_cita), self.cb_estado.get()):
            raise ErrorOperacion("No se pudo cambiar el estado de la cita.")
        self.refrescar()

    @con_errores
    def eliminar_por_error(self):
        id_cita = seleccionado(self.tabla, "Elige una cita de la tabla para eliminarla.")
        if id_cita is None:
            return
        if not messagebox.askyesno(
            "Confirmar", "Esto borra la cita por completo (no es cancelarla, es borrar el registro).\n¿Continuar?",
        ):
            return
        if not Cita.eliminar_cita_por_error(int(id_cita)):
            raise ErrorOperacion("No se pudo eliminar la cita.")
        self.refrescar()


# ----------------------------------------------------------------------
# Ventas
# ----------------------------------------------------------------------
class PanelVentas(ttk.Frame):
    def __init__(self, padre, usuario_actual):
        super().__init__(padre, padding=14)
        self.id_usuario = usuario_actual["id_usuario"]
        self.carrito = []
        self.total = Decimal("0")
        self.precios_servicios = {}
        self.datos_productos = {}
        self.var_precio_servicio = tk.StringVar()
        self.var_precio_producto = tk.StringVar()
        self.var_cantidad = tk.StringVar(value="1")
        self.var_stock = tk.StringVar()
        self.var_total = tk.StringVar(value=f"Total  {dinero(0)}")

        izquierda = ttk.Frame(self)
        izquierda.pack(side="left", fill="y", padx=(0, 16))
        derecha = ttk.Frame(self)
        derecha.pack(side="left", fill="both", expand=True)

        caja = ttk.LabelFrame(izquierda, text=" Venta ", padding=10)
        caja.pack(fill="x")
        ttk.Label(caja, text="Cliente").pack(anchor="w")
        self.cb_cliente = ComboConIds(caja, width=34)
        self.cb_cliente.pack(fill="x")
        ttk.Label(caja, text="Método de pago").pack(anchor="w", pady=(8, 0))
        self.cb_pago = ttk.Combobox(caja, values=METODOS_PAGO, state="readonly", width=34)
        self.cb_pago.set(METODOS_PAGO[0])
        self.cb_pago.pack(fill="x")

        caja = ttk.LabelFrame(izquierda, text=" Agregar servicio ", padding=10)
        caja.pack(fill="x", pady=12)
        ttk.Label(caja, text="Servicio").pack(anchor="w")
        self.cb_servicio = ComboConIds(caja, width=34)
        self.cb_servicio.pack(fill="x")
        self.cb_servicio.bind("<<ComboboxSelected>>", self.al_elegir_servicio)
        ttk.Label(caja, text="Barbero que lo realizó").pack(anchor="w", pady=(8, 0))
        self.cb_empleado = ComboConIds(caja, width=34)
        self.cb_empleado.pack(fill="x")
        ttk.Label(caja, text="Precio a cobrar").pack(anchor="w", pady=(8, 0))
        EntradaValidada(caja, tipo="decimal", textvariable=self.var_precio_servicio).pack(fill="x")
        BotonDegradado(caja, text="Agregar servicio al ticket", command=self.agregar_servicio).pack(fill="x", pady=(10, 0))

        caja = ttk.LabelFrame(izquierda, text=" Agregar producto ", padding=10)
        caja.pack(fill="x")
        ttk.Label(caja, text="Producto").pack(anchor="w")
        self.cb_producto = ComboConIds(caja, width=34)
        self.cb_producto.pack(fill="x")
        self.cb_producto.bind("<<ComboboxSelected>>", self.al_elegir_producto)
        fila = ttk.Frame(caja)
        fila.pack(fill="x", pady=(8, 0))
        ttk.Label(fila, text="Cantidad").pack(side="left")
        ttk.Spinbox(fila, from_=1, to=999, textvariable=self.var_cantidad, width=6).pack(side="left", padx=(6, 12))
        ttk.Label(fila, textvariable=self.var_stock, foreground=TEXTO_SUAVE).pack(side="left")
        ttk.Label(caja, text="Precio unitario").pack(anchor="w", pady=(8, 0))
        EntradaValidada(caja, tipo="decimal", textvariable=self.var_precio_producto).pack(fill="x")
        BotonDegradado(caja, text="Agregar producto al ticket", command=self.agregar_producto).pack(fill="x", pady=(10, 0))

        ttk.Label(derecha, text="Ticket", style="Encabezado.TLabel").pack(anchor="w")
        contenedor, self.tabla = crear_tabla(derecha, [
            ("tipo", "Tipo", 80, "w"), ("concepto", "Concepto", 220, "w"), ("detalle", "Detalle", 150, "w"),
            ("cantidad", "Cant.", 60, "e"), ("precio", "Precio", 100, "e"), ("subtotal", "Subtotal", 110, "e"),
        ], altura=13)
        contenedor.pack(fill="both", expand=True, pady=(6, 10))

        pie = ttk.Frame(derecha)
        pie.pack(fill="x")
        ttk.Label(pie, textvariable=self.var_total, style="Total.TLabel").pack(side="left")
        BotonDegradado(pie, text="Cobrar y registrar venta", command=self.cobrar).pack(side="right")
        ttk.Button(pie, text="Vaciar", command=self.vaciar).pack(side="right", padx=6)
        ttk.Button(pie, text="Quitar renglón", command=self.quitar).pack(side="right")

        buscar = ttk.LabelFrame(derecha, text=" Buscar / cancelar una venta por folio ", padding=10)
        buscar.pack(fill="x", pady=(14, 0))
        self.var_folio = tk.StringVar()
        self.var_resultado_folio = tk.StringVar(value="Escribe el número de folio (#) y presiona Buscar.")
        fila = ttk.Frame(buscar)
        fila.pack(fill="x")
        ttk.Label(fila, text="Folio #").pack(side="left")
        EntradaValidada(fila, tipo="entero", textvariable=self.var_folio, width=10).pack(side="left", padx=(6, 10))
        ttk.Button(fila, text="Buscar", command=self.buscar_folio).pack(side="left")
        ttk.Button(fila, text="Cancelar esta venta", command=self.cancelar_folio).pack(side="left", padx=6)
        ttk.Label(buscar, textvariable=self.var_resultado_folio, wraplength=560, justify="left", foreground=TEXTO_SUAVE).pack(anchor="w", pady=(8, 0))

    @con_errores
    def refrescar(self):
        clientes = [(None, "Mostrador (sin cliente)")] + [(f["id_cliente"], nombre_completo(f)) for f in Cliente.obtener_todos_los_clientes()]
        self.cb_cliente.cargar(clientes)
        if not self.cb_cliente.get():
            self.cb_cliente.current(0)

        servicios = Servicio.obtener_todos_los_servicios()
        self.precios_servicios = {f["id_servicio"]: f["precio_actual"] for f in servicios}
        self.cb_servicio.cargar([(f["id_servicio"], f["nombre_servicio"]) for f in servicios])
        self.cb_empleado.cargar([(f["id_empleado"], nombre_completo(f)) for f in Empleado.obtener_empleados_activos()])

        productos = Producto.obtener_todos_los_productos()
        self.datos_productos = {f["id_producto"]: f for f in productos}
        self.cb_producto.cargar([(f["id_producto"], f["nombre_producto"]) for f in productos])

    def al_elegir_servicio(self, _evento=None):
        precio = self.precios_servicios.get(self.cb_servicio.valor())
        if precio is not None:
            self.var_precio_servicio.set(str(precio))

    def al_elegir_producto(self, _evento=None):
        datos = self.datos_productos.get(self.cb_producto.valor())
        if datos:
            self.var_precio_producto.set(str(datos["precio_venta_actual"]))
            self.var_stock.set(f"En existencia: {datos['stock_total']}")

    @con_errores
    def agregar_servicio(self):
        id_servicio, id_empleado = self.cb_servicio.valor(), self.cb_empleado.valor()
        if id_servicio is None or id_empleado is None:
            raise ValueError("Elige el servicio y el barbero que lo realizó.")
        precio = convertir(self.var_precio_servicio.get(), "decimal", "Precio a cobrar")
        self.carrito.append({
            "tipo": "Servicio", "id": id_servicio, "concepto": self.cb_servicio.get(),
            "id_empleado": id_empleado, "detalle": self.cb_empleado.get(), "cantidad": 1, "precio": precio,
        })
        self.redibujar()

    @con_errores
    def agregar_producto(self):
        id_producto = self.cb_producto.valor()
        if id_producto is None:
            raise ValueError("Elige un producto.")
        cantidad = convertir(self.var_cantidad.get(), "entero", "Cantidad")
        if cantidad < 1:
            raise ValueError("La cantidad debe ser de al menos 1.")
        precio = convertir(self.var_precio_producto.get(), "decimal", "Precio unitario")

        stock = self.datos_productos[id_producto]["stock_total"]
        en_ticket = sum(x["cantidad"] for x in self.carrito if x["tipo"] == "Producto" and x["id"] == id_producto)
        if en_ticket + cantidad > stock:
            raise ValueError(f"No hay suficiente inventario: quedan {stock} y ya tienes {en_ticket} en el ticket.")

        self.carrito.append({
            "tipo": "Producto", "id": id_producto, "concepto": self.cb_producto.get(),
            "id_empleado": None, "detalle": self.datos_productos[id_producto]["marca"], "cantidad": cantidad, "precio": precio,
        })
        self.redibujar()

    def redibujar(self):
        self.tabla.delete(*self.tabla.get_children())
        self.total = Decimal("0")
        for i, x in enumerate(self.carrito):
            subtotal = x["precio"] * x["cantidad"]
            self.total += subtotal
            self.tabla.insert("", "end", tags=("par" if i % 2 == 0 else "impar",), values=(
                x["tipo"], x["concepto"], x["detalle"], x["cantidad"], dinero(x["precio"]), dinero(subtotal),
            ))
        self.var_total.set(f"Total  {dinero(self.total)}")

    def quitar(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showinfo("Falta una selección", "Elige un renglón del ticket para quitarlo.")
            return
        del self.carrito[self.tabla.index(seleccion[0])]
        self.redibujar()

    def vaciar(self):
        self.carrito.clear()
        self.redibujar()

    @con_errores
    def cobrar(self):
        if not self.carrito:
            raise ValueError("El ticket está vacío. Agrega al menos un servicio o producto.")
        if not messagebox.askyesno("Cobrar", f"El total es {dinero(self.total)}.\n¿Registrar la venta?"):
            return
        lista_servicios = [
            {"id_servicio": x["id"], "id_empleado": x["id_empleado"], "precio_cobrado": x["precio"]}
            for x in self.carrito if x["tipo"] == "Servicio"
        ]
        lista_productos = [
            {"id_producto": x["id"], "cantidad": x["cantidad"], "precio_cobrado": x["precio"]}
            for x in self.carrito if x["tipo"] == "Producto"
        ]
        id_venta = Venta.registrar_venta(
            self.cb_cliente.valor(), self.id_usuario, self.cb_pago.get(), float(self.total), lista_servicios, lista_productos,
        )
        if id_venta is None:
            raise ErrorOperacion("No se pudo registrar la venta (puede ser falta de stock o un dato inválido).")
        messagebox.showinfo("Venta registrada", f"Venta #{id_venta} registrada por {dinero(self.total)}.")
        self.vaciar()
        self.var_stock.set("")
        self.refrescar()

    @con_errores
    def buscar_folio(self):
        texto = self.var_folio.get().strip()
        if not texto.isdigit():
            raise ValueError("Escribe el número de folio de la venta (solo dígitos).")
        detalle = Venta.obtener_detalle_ticket(int(texto))
        if not detalle:
            self.var_resultado_folio.set(f"No se encontró ninguna venta con el folio #{texto}.")
            return
        ticket = detalle["ticket"]
        lineas = [f"Venta #{ticket['id_venta']} · {ticket['fecha_hora']} · {ticket['metodo_pago']} · Total: {dinero(ticket['total'])}"]
        cliente = ticket.get("cliente_nombres")
        lineas.append(f"Cliente: {cliente} {ticket.get('cliente_apellido', '')}" if cliente else "Cliente: Mostrador (sin cliente)")
        for s in detalle["servicios"]:
            lineas.append(f"  Servicio: {s['nombre_servicio']} — {dinero(s['precio_cobrado'])} (barbero: {s['barbero']})")
        for p in detalle["productos"]:
            lineas.append(f"  Producto: {p['nombre_producto']} x{p['cantidad']} — {dinero(p['precio_cobrado'])} c/u")
        self.var_resultado_folio.set("\n".join(lineas))

    @con_errores
    def cancelar_folio(self):
        texto = self.var_folio.get().strip()
        if not texto.isdigit():
            raise ValueError("Escribe el número de folio de la venta que quieres cancelar.")
        if not messagebox.askyesno(
            "Confirmar cancelación",
            f"Esto borra la venta #{texto} por completo: regresa los productos al inventario y "
            "quita la comisión que generó. No se puede deshacer. ¿Continuar?",
        ):
            return
        if not Venta.cancelar_venta_por_error(int(texto)):
            raise ErrorOperacion("No se pudo cancelar esa venta (revisa que el folio exista).")
        self.var_resultado_folio.set(f"Venta #{texto} cancelada. Inventario restaurado.")
        self.var_folio.set("")
        self.refrescar()


# ----------------------------------------------------------------------
# Clientes
# ----------------------------------------------------------------------
class PanelClientes(ttk.Frame):
    def __init__(self, padre):
        super().__init__(padre, padding=14)
        self.filas = {}
        self.cliente_actual = None
        self.var_nombres = tk.StringVar()
        self.var_apellido1 = tk.StringVar()
        self.var_apellido2 = tk.StringVar()
        self.var_telefono = tk.StringVar()
        self.var_corte = tk.StringVar()
        self.var_reactivar = tk.StringVar()
        self.var_busqueda = tk.StringVar()

        formulario = ttk.LabelFrame(self, text=" Datos del cliente ", padding=12)
        formulario.pack(fill="x")
        campos = [
            ("Nombre(s) *", self.var_nombres), ("Apellido paterno *", self.var_apellido1),
            ("Apellido materno", self.var_apellido2), ("Teléfono *", self.var_telefono)
        ]
        for i, (texto, var) in enumerate(campos):
            ttk.Label(formulario, text=texto).grid(row=0, column=i, sticky="w", padx=(0, 4))
            
            tipo_val = "texto"
            if "Teléfono" in texto:
                tipo_val = "entero"
            elif "Nombre" in texto or "Apellido" in texto:
                tipo_val = "letras"
                
            EntradaValidada(formulario, tipo=tipo_val, textvariable=var, width=18).grid(row=1, column=i, sticky="w", padx=(0, 16), pady=(0, 10))

        ttk.Label(formulario, text="Corte preferido").grid(row=0, column=4, sticky="w", padx=(0, 4))
        self.cb_corte = ttk.Combobox(formulario, textvariable=self.var_corte, width=18, values=[
            "Fade / Degradado", "Casquete Corto", "Casquete Regular", "Mullet",
            "Taper Fade", "Buzz Cut (Rapado)", "Corte Clásico a Tijera", "Texturizado", "Otro"
        ])
        self.cb_corte.grid(row=1, column=4, sticky="w", padx=(0, 16), pady=(0, 10))

        botones = ttk.Frame(formulario)
        botones.grid(row=2, column=0, columnspan=5, sticky="w")
        BotonDegradado(botones, text="Registrar cliente", command=self.registrar).pack(side="left")
        ttk.Button(botones, text="Guardar cambios del elegido", command=self.guardar_cambios).pack(side="left", padx=6)
        ttk.Button(botones, text="Dar de baja al elegido", command=self.dar_de_baja).pack(side="left")
        ttk.Button(botones, text="Eliminar por error", command=self.eliminar_por_error).pack(side="left", padx=6)
        ttk.Button(botones, text="Limpiar", command=self.limpiar).pack(side="left")
        ttk.Label(botones, text="   Reactivar por ID:").pack(side="left", padx=(20, 4))
        EntradaValidada(botones, tipo="entero", textvariable=self.var_reactivar, width=6).pack(side="left")
        ttk.Button(botones, text="Reactivar", command=self.reactivar).pack(side="left", padx=6)

        barra = ttk.Frame(self)
        barra.pack(fill="x", pady=(14, 6))
        ttk.Label(barra, text="Buscar por nombre").pack(side="left")
        entrada = EntradaValidada(barra, tipo="letras", textvariable=self.var_busqueda, width=24)
        entrada.pack(side="left", padx=8)
        entrada.bind("<KeyRelease>", lambda _e: self.pintar_tabla())
        ttk.Button(barra, text="Actualizar", command=self.refrescar).pack(side="right")

        contenedor, self.tabla = crear_tabla(self, [
            ("id", "ID", 0, "w"), ("nombre", "Nombre", 260, "w"), ("telefono", "Teléfono", 130, "w"), ("corte", "Corte preferido", 220, "w"),
        ], altura=6)
        contenedor.pack(fill="x")
        self.tabla.bind("<<TreeviewSelect>>", self.al_seleccionar)

        self.subpestanas = ttk.Notebook(self)
        self.subpestanas.pack(fill="both", expand=True, pady=(14, 0))

        pestana_tickets = ttk.Frame(self.subpestanas, padding=8)
        contenedor, self.tabla_tickets = crear_tabla(pestana_tickets, [
            ("id", "Folio", 70, "w"), ("fecha", "Fecha y hora", 160, "w"), ("total", "Total", 100, "e"), ("pago", "Método de pago", 140, "w"),
        ], altura=5)
        contenedor.pack(fill="both", expand=True)
        self.subpestanas.add(pestana_tickets, text="Tickets")

        pestana_citas = ttk.Frame(self.subpestanas, padding=8)
        contenedor, self.tabla_citas = crear_tabla(pestana_citas, [
            ("fecha", "Fecha", 100, "w"), ("hora", "Hora", 80, "w"), ("estado", "Estado", 100, "w"),
            ("servicio", "Servicio", 160, "w"), ("barbero", "Barbero", 160, "w"),
        ], altura=5)
        contenedor.pack(fill="both", expand=True)
        self.subpestanas.add(pestana_citas, text="Citas pasadas")

        pestana_notas = ttk.Frame(self.subpestanas, padding=8)
        contenedor, self.tabla_notas = crear_tabla(pestana_notas, [
            ("id", "ID", 0, "w"), ("fecha", "Fecha", 100, "w"), ("nota", "Nota", 360, "w"), ("barbero", "Anotó", 150, "w"),
        ], altura=4)
        contenedor.pack(fill="both", expand=True)
        self.tabla_notas.bind("<<TreeviewSelect>>", self.al_seleccionar_nota)
        captura = ttk.Frame(pestana_notas)
        captura.pack(fill="x", pady=(8, 0))
        self.notas_cargadas = {}
        self.var_texto_nota = tk.StringVar()
        self.cb_empleado_nota = ComboConIds(captura, width=22)
        ttk.Label(captura, text="Barbero que anota").pack(side="left")
        self.cb_empleado_nota.pack(side="left", padx=(6, 14))
        BotonDegradado(captura, text="Agregar nota nueva", command=self.agregar_nota).pack(side="right")
        ttk.Button(captura, text="Guardar edición", command=self.editar_nota).pack(side="right", padx=6)
        ttk.Button(captura, text="Eliminar nota", command=self.eliminar_nota).pack(side="right")
        ttk.Entry(captura, textvariable=self.var_texto_nota).pack(side="left", padx=(6, 0), fill="x", expand=True)
        ttk.Label(
            pestana_notas, foreground=TEXTO_SUAVE,
            text='Elige una nota de la tabla para editarla o eliminarla; escribe texto nuevo (sin elegir ninguna) y presiona "Agregar nota nueva" para crear una.',
        ).pack(anchor="w", pady=(6, 0))
        self.subpestanas.add(pestana_notas, text="Notas")

    @con_errores
    def refrescar(self):
        self.clientes_cargados = Cliente.obtener_todos_los_clientes()
        self.cb_empleado_nota.cargar([(f["id_empleado"], nombre_completo(f)) for f in Empleado.obtener_empleados_activos()])
        self.pintar_tabla()

    def pintar_tabla(self):
        texto = self.var_busqueda.get().strip().lower()
        filas = self.clientes_cargados
        for f in filas:
            f["nombre"] = nombre_completo(f)
        if texto:
            filas = [f for f in filas if texto in f["nombre"].lower()]
        self.filas = llenar_tabla(self.tabla, filas, claves=["id_cliente", "nombre", "telefono", "corte_preferido"])

    def al_seleccionar(self, _evento=None):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        fila = self.filas[seleccion[0]]
        self.cliente_actual = fila
        self.var_nombres.set(fila.get("nombres", ""))
        self.var_apellido1.set(fila.get("primer_apellido", ""))
        self.var_apellido2.set(fila.get("segundo_apellido") or "")
        self.var_telefono.set(fila.get("telefono", ""))
        self.var_corte.set(fila.get("corte_preferido") or "")
        self.cargar_historial(fila["id_cliente"])

    @con_errores
    def cargar_historial(self, id_cliente):
        llenar_tabla(self.tabla_tickets, HistorialCliente.obtener_tickets(id_cliente),
                     claves=["id_venta", "fecha_hora", "total", "metodo_pago"], formatos=[None, None, dinero, None])
        llenar_tabla(self.tabla_citas, [dict(f, _id=i) for i, f in enumerate(HistorialCliente.obtener_citas_pasadas(id_cliente))],
                     claves=["_id", "fecha_cita", "hora_cita", "estado", "nombre_servicio", "barbero"],
                     formatos=[None, None, formatear_hora, None, None, None])
        self.notas_cargadas = llenar_tabla(self.tabla_notas, Nota.obtener_notas_cliente(id_cliente),
                                            claves=["id_nota", "fecha_nota", "descripcion", "escrito_por"])

    @con_errores
    def registrar(self):
        nombres = convertir(self.var_nombres.get(), "texto", "Nombre(s)", True, 50)
        apellido1 = convertir(self.var_apellido1.get(), "texto", "Apellido paterno", True, 50)
        apellido2 = convertir(self.var_apellido2.get(), "texto", "Apellido materno", False, 50)
        telefono = convertir(self.var_telefono.get(), "texto", "Teléfono", True, 15)
        corte = convertir(self.var_corte.get(), "texto", "Corte preferido", False, 100)
        if not Cliente.registrar_cliente(nombres, apellido1, apellido2, telefono, corte):
            raise ErrorOperacion("No se pudo registrar el cliente (revisa que el teléfono no esté repetido).")
        self.limpiar()
        self.refrescar()

    @con_errores
    def guardar_cambios(self):
        if not self.cliente_actual:
            raise ValueError("Elige un cliente de la tabla para editarlo.")
        nombres = convertir(self.var_nombres.get(), "texto", "Nombre(s)", True, 50)
        apellido1 = convertir(self.var_apellido1.get(), "texto", "Apellido paterno", True, 50)
        apellido2 = convertir(self.var_apellido2.get(), "texto", "Apellido materno", False, 50)
        telefono = convertir(self.var_telefono.get(), "texto", "Teléfono", True, 15)
        corte = convertir(self.var_corte.get(), "texto", "Corte preferido", False, 100)
        if not Cliente.editar_cliente(self.cliente_actual["id_cliente"], nombres, apellido1, apellido2, telefono, corte):
            raise ErrorOperacion("No se pudo guardar los cambios (revisa que el teléfono no esté repetido).")
        self.limpiar()
        self.refrescar()

    @con_errores
    def eliminar_por_error(self):
        id_cliente = seleccionado(self.tabla, "Elige un cliente de la tabla para eliminarlo.")
        if id_cliente is None:
            return
        if not messagebox.askyesno(
            "Confirmar",
            "Esto borra al cliente por completo (no es darlo de baja). Solo funciona si nunca ha "
            "tenido una venta registrada. ¿Continuar?",
        ):
            return
        if not Cliente.eliminar_cliente_por_error(int(id_cliente)):
            raise ErrorOperacion("No se pudo eliminar (probablemente ya tiene ventas registradas; usa \"Dar de baja\" en su lugar).")
        self.limpiar()
        self.refrescar()

    @con_errores
    def dar_de_baja(self):
        id_cliente = seleccionado(self.tabla, "Elige un cliente de la tabla para darlo de baja.")
        if id_cliente is None:
            return
        if not messagebox.askyesno("Confirmar", "¿Dar de baja al cliente seleccionado? Dejará de aparecer en la lista."):
            return
        Cliente.dar_de_baja(int(id_cliente))
        self.limpiar()
        self.refrescar()

    @con_errores
    def reactivar(self):
        texto = self.var_reactivar.get().strip()
        if not texto.isdigit():
            raise ValueError("Escribe el ID numérico del cliente que quieres reactivar.")
        Cliente.reactivar_cliente(int(texto))
        self.var_reactivar.set("")
        self.refrescar()

    def al_seleccionar_nota(self, _evento=None):
        seleccion = self.tabla_notas.selection()
        if seleccion:
            self.var_texto_nota.set(self.notas_cargadas[seleccion[0]]["descripcion"])

    @con_errores
    def agregar_nota(self):
        if not self.cliente_actual:
            raise ValueError("Primero elige un cliente en la tabla de arriba.")
        id_empleado = self.cb_empleado_nota.valor()
        if id_empleado is None:
            raise ValueError("Elige qué barbero deja la nota.")
        descripcion = convertir(self.var_texto_nota.get(), "texto", "Nota", True, 1000)
        if not Nota.agregar_nota(self.cliente_actual["id_cliente"], id_empleado, descripcion):
            raise ErrorOperacion("No se pudo agregar la nota.")
        self.var_texto_nota.set("")
        self.tabla_notas.selection_remove(*self.tabla_notas.selection())
        self.cargar_historial(self.cliente_actual["id_cliente"])

    @con_errores
    def editar_nota(self):
        id_nota = seleccionado(self.tabla_notas, "Elige una nota de la tabla para editarla.")
        if id_nota is None:
            return
        descripcion = convertir(self.var_texto_nota.get(), "texto", "Nota", True, 1000)
        if not Nota.editar_nota(int(id_nota), descripcion):
            raise ErrorOperacion("No se pudo editar la nota.")
        self.cargar_historial(self.cliente_actual["id_cliente"])

    @con_errores
    def eliminar_nota(self):
        id_nota = seleccionado(self.tabla_notas, "Elige una nota de la tabla para eliminarla.")
        if id_nota is None:
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar esta nota por completo?"):
            return
        if not Nota.eliminar_nota_por_error(int(id_nota)):
            raise ErrorOperacion("No se pudo eliminar la nota.")
        self.var_texto_nota.set("")
        self.cargar_historial(self.cliente_actual["id_cliente"])

    def limpiar(self):
        for var in (self.var_nombres, self.var_apellido1, self.var_apellido2, self.var_telefono, self.var_corte):
            var.set("")
        self.tabla.selection_remove(*self.tabla.selection())


# ----------------------------------------------------------------------
# Empleados
# ----------------------------------------------------------------------
class PanelEmpleados(ttk.Frame):
    def __init__(self, padre):
        super().__init__(padre, padding=14)
        self.filas = {}
        self.empleado_actual = None
        self.campos = {
            "nombres": tk.StringVar(), "primer_apellido": tk.StringVar(), "segundo_apellido": tk.StringVar(),
            "curp": tk.StringVar(), "telefono": tk.StringVar(), "correo": tk.StringVar(),
            "calle": tk.StringVar(), "num_exterior": tk.StringVar(), "num_interior": tk.StringVar(),
            "colonia": tk.StringVar(), "cp": tk.StringVar(), "puesto": tk.StringVar(),
            "salario_base": tk.StringVar(), "porcentaje_comision": tk.StringVar(),
        }
        self.var_reactivar = tk.StringVar()

        formulario = ttk.LabelFrame(self, text=" Datos del empleado ", padding=12)
        formulario.pack(fill="x")
        etiquetas = [
            ("Nombre(s) *", "nombres"), ("Apellido paterno *", "primer_apellido"), ("Apellido materno", "segundo_apellido"), ("CURP *", "curp"),
            ("Teléfono *", "telefono"), ("Correo", "correo"), ("Puesto *", "puesto"), ("Salario base", "salario_base"),
            ("Calle *", "calle"), ("Núm. exterior *", "num_exterior"), ("Núm. interior", "num_interior"), ("Colonia *", "colonia"),
            ("C.P. *", "cp"), ("Comisión % *", "porcentaje_comision"),
        ]
        for i, (texto, clave) in enumerate(etiquetas):
            fila, columna = divmod(i, 4)
            ttk.Label(formulario, text=texto).grid(row=fila * 2, column=columna, sticky="w", padx=(0, 6))
            
            tipo_val = "texto"
            if clave in ("telefono", "cp"): 
                tipo_val = "entero"
            elif clave in ("salario_base", "porcentaje_comision"): 
                tipo_val = "decimal"
            elif clave in ("nombres", "primer_apellido", "segundo_apellido", "puesto"):
                tipo_val = "letras"
                
            EntradaValidada(formulario, tipo=tipo_val, textvariable=self.campos[clave], width=18).grid(row=fila * 2 + 1, column=columna, sticky="w", padx=(0, 16), pady=(0, 8))

        botones = ttk.Frame(formulario)
        botones.grid(row=8, column=0, columnspan=4, sticky="w", pady=(6, 0))
        BotonDegradado(botones, text="Registrar empleado", command=self.registrar).pack(side="left")
        ttk.Button(botones, text="Guardar cambios del elegido", command=self.guardar_cambios).pack(side="left", padx=6)
        ttk.Button(botones, text="Dar de baja al elegido", command=self.dar_de_baja).pack(side="left")
        ttk.Button(botones, text="Eliminar por error", command=self.eliminar_por_error).pack(side="left", padx=6)
        ttk.Button(botones, text="Limpiar", command=self.limpiar).pack(side="left")
        ttk.Label(botones, text="   Reactivar por ID:").pack(side="left", padx=(20, 4))
        EntradaValidada(botones, tipo="entero", textvariable=self.var_reactivar, width=6).pack(side="left")
        ttk.Button(botones, text="Reactivar", command=self.reactivar).pack(side="left", padx=6)

        contenedor, self.tabla = crear_tabla(self, [
            ("id", "ID", 0, "w"), ("nombre", "Nombre", 220, "w"), ("puesto", "Puesto", 130, "w"),
            ("telefono", "Teléfono", 110, "w"), ("comision", "Comisión", 90, "e"), ("salario", "Salario base", 110, "e"),
        ], altura=6)
        contenedor.pack(fill="x", pady=(14, 0))
        self.tabla.bind("<<TreeviewSelect>>", self.al_seleccionar)

        self.subpestanas = ttk.Notebook(self)
        self.subpestanas.pack(fill="both", expand=True, pady=(14, 0))

        pestana_citas = ttk.Frame(self.subpestanas, padding=8)
        contenedor, self.tabla_citas = crear_tabla(pestana_citas, [
            ("fecha", "Fecha", 100, "w"), ("hora", "Hora", 80, "w"), ("estado", "Estado", 100, "w"),
            ("servicio", "Servicio", 160, "w"), ("cliente", "Cliente", 200, "w"),
        ], altura=5)
        contenedor.pack(fill="both", expand=True)
        self.subpestanas.add(pestana_citas, text="Citas atendidas")

        pestana_servicios = ttk.Frame(self.subpestanas, padding=8)
        barra = ttk.Frame(pestana_servicios)
        barra.pack(fill="x")
        self.cb_periodo_servicios = ttk.Combobox(barra, values=["Semana", "Mes", "Todo"], state="readonly", width=12)
        self.cb_periodo_servicios.set("Semana")
        ttk.Label(barra, text="Periodo").pack(side="left")
        self.cb_periodo_servicios.pack(side="left", padx=8)
        ttk.Button(barra, text="Consultar", command=self.consultar_servicios).pack(side="left")
        contenedor, self.tabla_servicios = crear_tabla(pestana_servicios, [
            ("fecha", "Fecha", 150, "w"), ("servicio", "Servicio", 180, "w"), ("precio", "Cobrado", 100, "e"),
        ], altura=4)
        contenedor.pack(fill="both", expand=True, pady=(8, 0))
        self.subpestanas.add(pestana_servicios, text="Servicios cobrados")

        pestana_nomina = ttk.Frame(self.subpestanas, padding=14)
        BotonDegradado(pestana_nomina, text="Calcular nómina de la semana actual", command=self.calcular_nomina).pack(anchor="w")
        self.var_nomina = tk.StringVar(value="Elige un empleado y presiona el botón.")
        ttk.Label(pestana_nomina, textvariable=self.var_nomina, font=("Segoe UI", 11), justify="left", wraplength=700).pack(anchor="w", pady=(14, 0))
        self.subpestanas.add(pestana_nomina, text="Nómina")

    @con_errores
    def refrescar(self):
        self.empleados_cargados = Empleado.obtener_empleados_activos()
        self.filas = llenar_tabla(
            self.tabla, [dict(f, nombre=nombre_completo(f)) for f in self.empleados_cargados],
            claves=["id_empleado", "nombre", "puesto", "telefono", "porcentaje_comision", "salario_base"],
            formatos=[None, None, None, None, lambda v: f"{v} %", dinero],
        )

    def al_seleccionar(self, _evento=None):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        fila = self.filas[seleccion[0]]
        self.empleado_actual = fila
        for clave, var in self.campos.items():
            if clave in ("salario_base", "porcentaje_comision"):
                var.set(str(fila.get(clave, "") or ""))
            else:
                var.set(fila.get(clave) or "")
        self.cargar_historial(fila["id_empleado"])

    @con_errores
    def cargar_historial(self, id_empleado):
        llenar_tabla(
            self.tabla_citas,
            [dict(f, _id=i, cliente=f"{f.get('nombre_cliente','')}_{f.get('apellido_cliente','')}".strip())
             for i, f in enumerate(HistorialEmpleado.obtener_citas_atendidas(id_empleado))],
            claves=["_id", "fecha_cita", "hora_cita", "estado", "nombre_servicio", "cliente"],
            formatos=[None, None, formatear_hora, None, None, None],
        )
        self.id_empleado_actual_historial = id_empleado
        self.consultar_servicios()

    @con_errores
    def consultar_servicios(self):
        if not self.empleado_actual:
            return
        periodo = {"Semana": "semana", "Mes": "mes", "Todo": "todo"}[self.cb_periodo_servicios.get()]
        filas = HistorialEmpleado.obtener_servicios_cobrados(self.empleado_actual["id_empleado"], periodo)
        llenar_tabla(self.tabla_servicios, [dict(f, _id=i) for i, f in enumerate(filas)],
                     claves=["_id", "fecha_hora", "nombre_servicio", "precio_cobrado"], formatos=[None, None, None, dinero])

    @con_errores
    def calcular_nomina(self):
        if not self.empleado_actual:
            raise ValueError("Primero elige un empleado en la tabla.")
        resultado = Nomina.calcular_pago_semanal(self.empleado_actual["id_empleado"])
        if "error" in resultado:
            raise ErrorOperacion(resultado["error"])
        self.var_nomina.set(
            f"Empleado: {resultado['empleado']}\n"
            f"Salario base: {dinero(resultado['salario_base'])}\n"
            f"Comisión: {resultado['porcentaje_comision']} sobre {dinero(resultado['total_generado_a_la_barberia'])} generados = {dinero(resultado['comision_ganada'])}\n"
            f"Total a pagar esta semana: {dinero(resultado['total_a_pagar'])}"
        )

    @con_errores
    def registrar(self):
        if not Empleado.registrar_empleado(*self._leer_formulario()):
            raise ErrorOperacion("No se pudo registrar el empleado (revisa que la CURP y el teléfono no estén repetidos).")
        self.limpiar()
        self.refrescar()

    def _leer_formulario(self):
        c = self.campos
        return (
            convertir(c["nombres"].get(), "texto", "Nombre(s)", True, 50),
            convertir(c["primer_apellido"].get(), "texto", "Apellido paterno", True, 50),
            convertir(c["segundo_apellido"].get(), "texto", "Apellido materno", False, 50),
            convertir(c["curp"].get(), "texto", "CURP", True, 18),
            convertir(c["telefono"].get(), "texto", "Teléfono", True, 15),
            convertir(c["correo"].get(), "texto", "Correo", False, 100),
            convertir(c["calle"].get(), "texto", "Calle", True, 100),
            convertir(c["num_exterior"].get(), "texto", "Número exterior", True, 10),
            convertir(c["num_interior"].get(), "texto", "Número interior", False, 10),
            convertir(c["colonia"].get(), "texto", "Colonia", True, 100),
            convertir(c["cp"].get(), "texto", "Código postal", True, 5),
            convertir(c["puesto"].get(), "texto", "Puesto", True, 50),
            float(convertir(c["salario_base"].get(), "decimal", "Salario base", False)),
            float(convertir(c["porcentaje_comision"].get(), "porcentaje", "Comisión", False)),
        )

    @con_errores
    def guardar_cambios(self):
        if not self.empleado_actual:
            raise ValueError("Elige un empleado de la tabla para editarlo.")
        if not Empleado.editar_empleado(self.empleado_actual["id_empleado"], *self._leer_formulario()):
            raise ErrorOperacion("No se pudo guardar los cambios (revisa que la CURP y el teléfono no estén repetidos).")
        self.limpiar()
        self.refrescar()

    @con_errores
    def eliminar_por_error(self):
        id_empleado = seleccionado(self.tabla, "Elige un empleado de la tabla para eliminarlo.")
        if id_empleado is None:
            return
        if not messagebox.askyesno(
            "Confirmar",
            "Esto borra al empleado por completo (no es darlo de baja). Solo funciona si nunca ha "
            "tenido citas, servicios cobrados o notas a su nombre. ¿Continuar?",
        ):
            return
        if not Empleado.eliminar_empleado_por_error(int(id_empleado)):
            raise ErrorOperacion("No se pudo eliminar (probablemente ya tiene historial; usa \"Dar de baja\" en su lugar).")
        self.limpiar()
        self.refrescar()

    @con_errores
    def dar_de_baja(self):
        id_empleado = seleccionado(self.tabla, "Elige un empleado de la tabla para darlo de baja.")
        if id_empleado is None:
            return
        if not messagebox.askyesno("Confirmar", "¿Dar de baja al empleado seleccionado?"):
            return
        Empleado.dar_de_baja(int(id_empleado))
        self.limpiar()
        self.refrescar()

    @con_errores
    def reactivar(self):
        texto = self.var_reactivar.get().strip()
        if not texto.isdigit():
            raise ValueError("Escribe el ID numérico del empleado que quieres reactivar.")
        Empleado.reactivar_empleado(int(texto))
        self.var_reactivar.set("")
        self.refrescar()

    def limpiar(self):
        for var in self.campos.values():
            var.set("")
        self.tabla.selection_remove(*self.tabla.selection())


# ----------------------------------------------------------------------
# Servicios
# ----------------------------------------------------------------------
class PanelServicios(ttk.Frame):
    def __init__(self, padre):
        super().__init__(padre, padding=14)
        self.filas = {}
        self.var_nombre = tk.StringVar()
        self.var_precio = tk.StringVar()
        self.var_duracion = tk.StringVar()

        formulario = ttk.LabelFrame(self, text=" Servicio ", padding=12)
        formulario.pack(fill="x")
        for i, (texto, var, ancho) in enumerate([
            ("Nombre *", self.var_nombre, 26), ("Precio *", self.var_precio, 14), ("Duración (minutos) *", self.var_duracion, 14),
        ]):
            ttk.Label(formulario, text=texto).grid(row=0, column=i, sticky="w", padx=(0, 6))
            
            tipo_val = "texto"
            if "Precio" in texto: tipo_val = "decimal"
            elif "Duración" in texto: tipo_val = "entero"
            
            EntradaValidada(formulario, tipo=tipo_val, textvariable=var, width=ancho).grid(row=1, column=i, sticky="w", padx=(0, 16))
            
        botones = ttk.Frame(formulario)
        botones.grid(row=2, column=0, columnspan=3, sticky="w", pady=(12, 0))
        BotonDegradado(botones, text="Registrar servicio", command=self.registrar).pack(side="left")
        ttk.Button(botones, text="Guardar cambios del elegido", command=self.guardar_cambios).pack(side="left", padx=6)
        ttk.Button(botones, text="Eliminar por error", command=self.eliminar_por_error).pack(side="left")
        ttk.Button(botones, text="Limpiar", command=self.limpiar).pack(side="left", padx=6)

        contenedor, self.tabla = crear_tabla(self, [
            ("id", "ID", 0, "w"), ("nombre", "Nombre", 300, "w"), ("precio", "Precio", 120, "e"), ("duracion", "Duración", 120, "e"),
        ], altura=12)
        contenedor.pack(fill="both", expand=True, pady=(14, 0))
        self.tabla.bind("<<TreeviewSelect>>", self.al_seleccionar)

    @con_errores
    def refrescar(self):
        self.filas = llenar_tabla(self.tabla, Servicio.obtener_todos_los_servicios(),
                                   claves=["id_servicio", "nombre_servicio", "precio_actual", "duracion_minutos"],
                                   formatos=[None, None, dinero, lambda v: f"{v} min"])

    def al_seleccionar(self, _evento=None):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        fila = self.filas[seleccion[0]]
        self.var_nombre.set(fila["nombre_servicio"])
        self.var_precio.set(str(fila["precio_actual"]))
        self.var_duracion.set(str(fila["duracion_minutos"]))

    @con_errores
    def registrar(self):
        nombre = convertir(self.var_nombre.get(), "texto", "Nombre", True, 100)
        precio = convertir(self.var_precio.get(), "decimal", "Precio")
        duracion = convertir(self.var_duracion.get(), "entero", "Duración")
        if not Servicio.registrar_servicio(nombre, precio, duracion):
            raise ErrorOperacion("No se pudo registrar el servicio.")
        self.limpiar()
        self.refrescar()

    @con_errores
    def guardar_cambios(self):
        id_servicio = seleccionado(self.tabla, "Elige un servicio de la tabla para editarlo.")
        if id_servicio is None:
            return
        nombre = convertir(self.var_nombre.get(), "texto", "Nombre", True, 100)
        precio = convertir(self.var_precio.get(), "decimal", "Precio")
        duracion = convertir(self.var_duracion.get(), "entero", "Duración")
        if not Servicio.editar_servicio(int(id_servicio), nombre, precio, duracion):
            raise ErrorOperacion("No se pudo guardar los cambios.")
        self.limpiar()
        self.refrescar()

    @con_errores
    def eliminar_por_error(self):
        id_servicio = seleccionado(self.tabla, "Elige un servicio de la tabla para eliminarlo.")
        if id_servicio is None:
            return
        if not messagebox.askyesno(
            "Confirmar",
            "Esto borra el servicio por completo. Solo funciona si nunca se ha usado en una cita ni en una venta.\n¿Continuar?",
        ):
            return
        if not Servicio.eliminar_servicio_por_error(int(id_servicio)):
            raise ErrorOperacion("No se pudo eliminar (probablemente ya tiene historial); edítalo en vez de borrarlo.")
        self.limpiar()
        self.refrescar()

    def limpiar(self):
        self.var_nombre.set(""); self.var_precio.set(""); self.var_duracion.set("")
        self.tabla.selection_remove(*self.tabla.selection())


# ----------------------------------------------------------------------
# Productos (+ entradas de inventario)
# ----------------------------------------------------------------------
class PanelProductos(ttk.Frame):
    def __init__(self, padre):
        super().__init__(padre, padding=14)
        self.filas = {}
        self.var_nombre = tk.StringVar()
        self.var_marca = tk.StringVar()
        self.var_precio = tk.StringVar()
        self.var_stock_inicial = tk.StringVar(value="0")
        self.var_nuevo_precio = tk.StringVar()

        formulario = ttk.LabelFrame(self, text=" Nuevo producto ", padding=12)
        formulario.pack(fill="x")
        for i, (texto, var, ancho) in enumerate([
            ("Nombre *", self.var_nombre, 22), ("Marca *", self.var_marca, 16),
            ("Precio de venta *", self.var_precio, 12), ("Stock inicial", self.var_stock_inicial, 10),
        ]):
            ttk.Label(formulario, text=texto).grid(row=0, column=i, sticky="w", padx=(0, 6))
            
            tipo_val = "texto"
            if "Precio" in texto: tipo_val = "decimal"
            elif "Stock" in texto: tipo_val = "entero"
            
            EntradaValidada(formulario, tipo=tipo_val, textvariable=var, width=ancho).grid(row=1, column=i, sticky="w", padx=(0, 16))
            
        botones = ttk.Frame(formulario)
        botones.grid(row=2, column=0, columnspan=4, sticky="w", pady=(10, 0))
        BotonDegradado(botones, text="Registrar producto", command=self.registrar).pack(side="left")
        ttk.Button(botones, text="Guardar nombre/marca del elegido", command=self.guardar_nombre_marca).pack(side="left", padx=6)
        ttk.Button(botones, text="Eliminar por error", command=self.eliminar_por_error).pack(side="left")
        ttk.Label(botones, text="   Nuevo precio del elegido:").pack(side="left", padx=(20, 4))
        EntradaValidada(botones, tipo="decimal", textvariable=self.var_nuevo_precio, width=10).pack(side="left")
        ttk.Button(botones, text="Actualizar precio", command=self.actualizar_precio).pack(side="left", padx=6)

        contenedor, self.tabla = crear_tabla(self, [
            ("id", "ID", 0, "w"), ("nombre", "Nombre", 220, "w"), ("marca", "Marca", 140, "w"),
            ("precio", "Precio", 100, "e"), ("stock", "Stock", 90, "e"),
        ], altura=6)
        contenedor.pack(fill="x", pady=(14, 0))
        self.tabla.bind("<<TreeviewSelect>>", self.al_seleccionar)

        entradas = ttk.LabelFrame(self, text=" Entrada de inventario (compra de mercancía) ", padding=12)
        entradas.pack(fill="x", pady=(14, 0))
        self.var_cantidad = tk.StringVar()
        self.var_costo = tk.StringVar()
        self.var_fecha_llegada = tk.StringVar(value=hoy())
        self.var_caducidad = tk.StringVar()
        for i, (texto, var, ancho) in enumerate([
            ("Fecha de llegada", self.var_fecha_llegada, 12), ("Cantidad *", self.var_cantidad, 10),
            ("Costo unitario *", self.var_costo, 12), ("Caducidad (opcional)", self.var_caducidad, 12),
        ]):
            ttk.Label(entradas, text=texto).grid(row=0, column=i, sticky="w", padx=(0, 6))
            
            tipo_val = "texto"
            if "Cantidad" in texto: tipo_val = "entero"
            elif "Costo" in texto: tipo_val = "decimal"
            
            EntradaValidada(entradas, tipo=tipo_val, textvariable=var, width=ancho).grid(row=1, column=i, sticky="w", padx=(0, 16))
            
        BotonDegradado(entradas, text="Registrar entrada (suma al stock)", command=self.registrar_entrada).grid(row=1, column=4, sticky="w")
        ttk.Button(entradas, text="Eliminar entrada por error (resta del stock)", command=self.eliminar_entrada_por_error).grid(row=1, column=5, sticky="w", padx=(10, 0))
        ttk.Label(entradas, text="Para registrar: usa el producto elegido en la tabla de arriba. Para eliminar: elige la entrada en la tabla de abajo.", foreground=TEXTO_SUAVE).grid(row=2, column=0, columnspan=6, sticky="w", pady=(6, 0))

        contenedor, self.tabla_entradas = crear_tabla(self, [
            ("id", "ID", 0, "w"), ("producto", "Producto", 180, "w"), ("marca", "Marca", 120, "w"),
            ("fecha", "Llegada", 100, "w"), ("cantidad", "Cantidad", 90, "e"), ("costo", "Costo unitario", 110, "e"), ("caduca", "Caducidad", 100, "w"),
        ], altura=6)
        contenedor.pack(fill="both", expand=True, pady=(10, 0))

    @con_errores
    def refrescar(self):
        self.filas = llenar_tabla(self.tabla, Producto.obtener_todos_los_productos(),
                                   claves=["id_producto", "nombre_producto", "marca", "precio_venta_actual", "stock_total"],
                                   formatos=[None, None, None, dinero, None])
        llenar_tabla(self.tabla_entradas, EntradaInventario.obtener_todas_las_entradas(),
                     claves=["id_entrada", "nombre_producto", "marca", "fecha_llegada", "cantidad", "costo_unitario", "fecha_caducidad"],
                     formatos=[None, None, None, None, None, dinero, None])

    def al_seleccionar(self, _evento=None):
        seleccion = self.tabla.selection()
        if seleccion:
            self.var_nuevo_precio.set(str(self.filas[seleccion[0]]["precio_venta_actual"]))

    @con_errores
    def registrar(self):
        nombre = convertir(self.var_nombre.get(), "texto", "Nombre", True, 100)
        marca = convertir(self.var_marca.get(), "texto", "Marca", True, 50)
        precio = convertir(self.var_precio.get(), "decimal", "Precio de venta")
        stock = convertir(self.var_stock_inicial.get(), "entero", "Stock inicial", False)
        if not Producto.registrar_producto(nombre, marca, precio, stock or 0):
            raise ErrorOperacion("No se pudo registrar el producto.")
        self.var_nombre.set(""); self.var_marca.set(""); self.var_precio.set(""); self.var_stock_inicial.set("0")
        self.refrescar()

    @con_errores
    def actualizar_precio(self):
        id_producto = seleccionado(self.tabla, "Elige un producto de la tabla.")
        if id_producto is None:
            return
        nuevo_precio = convertir(self.var_nuevo_precio.get(), "decimal", "Nuevo precio")
        if not Producto.actualizar_precio_producto(int(id_producto), nuevo_precio):
            raise ErrorOperacion("No se pudo actualizar el precio.")
        self.refrescar()

    @con_errores
    def guardar_nombre_marca(self):
        id_producto = seleccionado(self.tabla, "Elige un producto de la tabla para editar su nombre o marca.")
        if id_producto is None:
            return
        nombre = convertir(self.var_nombre.get(), "texto", "Nombre", True, 100)
        marca = convertir(self.var_marca.get(), "texto", "Marca", True, 50)
        if not Producto.editar_producto(int(id_producto), nombre, marca):
            raise ErrorOperacion("No se pudo guardar los cambios.")
        self.limpiar_formulario()
        self.refrescar()

    @con_errores
    def eliminar_por_error(self):
        id_producto = seleccionado(self.tabla, "Elige un producto de la tabla para eliminarlo.")
        if id_producto is None:
            return
        if not messagebox.askyesno(
            "Confirmar",
            "Esto borra el producto por completo. Solo funciona si nunca ha tenido entradas de "
            "inventario ni ventas. ¿Continuar?",
        ):
            return
        if not Producto.eliminar_producto_por_error(int(id_producto)):
            raise ErrorOperacion("No se pudo eliminar (probablemente ya tiene historial de compras o ventas).")
        self.limpiar_formulario()
        self.refrescar()

    def limpiar_formulario(self):
        self.var_nombre.set(""); self.var_marca.set(""); self.var_precio.set(""); self.var_stock_inicial.set("0")
        self.var_nuevo_precio.set("")
        self.tabla.selection_remove(*self.tabla.selection())

    @con_errores
    def registrar_entrada(self):
        id_producto = seleccionado(self.tabla, "Elige un producto de la tabla para registrarle una entrada.")
        if id_producto is None:
            return
        fecha = validar_fecha(self.var_fecha_llegada.get())
        cantidad = convertir(self.var_cantidad.get(), "entero", "Cantidad")
        if cantidad < 1:
            raise ValueError("La cantidad debe ser de al menos 1.")
        costo = convertir(self.var_costo.get(), "decimal", "Costo unitario")
        caducidad = validar_fecha(self.var_caducidad.get(), "La caducidad", obligatorio=False)
        if not EntradaInventario.registrar_entrada(int(id_producto), fecha.isoformat(), cantidad, costo, caducidad.isoformat() if caducidad else None):
            raise ErrorOperacion("No se pudo registrar la entrada.")
        self.var_cantidad.set(""); self.var_costo.set(""); self.var_caducidad.set("")
        self.refrescar()

    @con_errores
    def eliminar_entrada_por_error(self):
        id_entrada = seleccionado(self.tabla_entradas, "Elige una entrada de la tabla de abajo para eliminarla.")
        if id_entrada is None:
            return
        if not messagebox.askyesno(
            "Confirmar",
            "Esto borra el registro de esa compra y le RESTA esa cantidad al stock del producto.\n"
            "Si parte de esa mercancía ya se vendió, no se podrá eliminar. ¿Continuar?",
        ):
            return
        if not EntradaInventario.eliminar_entrada_por_error(int(id_entrada)):
            raise ErrorOperacion("No se pudo eliminar la entrada (probablemente ya se vendió parte de esa mercancía).")
        self.refrescar()


# ----------------------------------------------------------------------
# Finanzas
# ----------------------------------------------------------------------
class PanelFinanzas(ttk.Frame):
    def __init__(self, padre):
        super().__init__(padre, padding=24)
        ttk.Label(self, text="Resumen de ingresos", style="Encabezado.TLabel").pack(anchor="w")

        barra = ttk.Frame(self)
        barra.pack(fill="x", pady=(10, 20))
        ttk.Label(barra, text="Periodo").pack(side="left")
        self.cb_periodo = ttk.Combobox(barra, values=["Día", "Semana", "Mes", "Año"], state="readonly", width=12)
        self.cb_periodo.set("Día")
        self.cb_periodo.pack(side="left", padx=8)
        BotonDegradado(barra, text="Consultar", command=self.consultar).pack(side="left")

        tarjetas = ttk.Frame(self)
        tarjetas.pack(fill="x")
        self.var_total = tk.StringVar(value=dinero(0))
        self.var_servicios = tk.StringVar(value=dinero(0))
        self.var_productos = tk.StringVar(value=dinero(0))
        for titulo, var in [("Total en caja", self.var_total), ("Por servicios (cortes)", self.var_servicios), ("Por productos", self.var_productos)]:
            caja = ttk.LabelFrame(tarjetas, text=f" {titulo} ", padding=16)
            caja.pack(side="left", padx=(0, 16))
            ttk.Label(caja, textvariable=var, style="Total.TLabel").pack()

        ttk.Separator(self).pack(fill="x", pady=24)

        # --- Corte de caja diario ---
        ttk.Label(self, text="Corte de caja diario", style="Encabezado.TLabel").pack(anchor="w")
        fila_corte = ttk.Frame(self)
        fila_corte.pack(fill="x", pady=(10, 10))
        self.var_fecha_corte = tk.StringVar(value=hoy())
        ttk.Label(fila_corte, text="Fecha").pack(side="left")
        ttk.Entry(fila_corte, textvariable=self.var_fecha_corte, width=12).pack(side="left", padx=(6, 10))
        BotonDegradado(fila_corte, text="Hacer corte", command=self.hacer_corte).pack(side="left")
        self.var_total_corte = tk.StringVar(value=dinero(0))
        ttk.Label(fila_corte, text="   Gran total del día:").pack(side="left", padx=(20, 4))
        ttk.Label(fila_corte, textvariable=self.var_total_corte, style="Total.TLabel").pack(side="left")

        contenedor, self.tabla_corte = crear_tabla(self, [
            ("id", "ID", 0, "w"), ("metodo", "Método de pago", 200, "w"), ("total", "Total recaudado", 160, "e"), ("tickets", "Número de tickets", 150, "e"),
        ], altura=4)
        contenedor.pack(fill="x", pady=(0, 10))

        ttk.Separator(self).pack(fill="x", pady=14)

        # --- Consulta por rango de fechas ---
        ttk.Label(self, text="Consultar por rango de fechas", style="Encabezado.TLabel").pack(anchor="w")
        fila_rango = ttk.Frame(self)
        fila_rango.pack(fill="x", pady=(10, 10))
        self.var_desde = tk.StringVar(value=hoy())
        self.var_hasta = tk.StringVar(value=hoy())
        ttk.Label(fila_rango, text="Desde").pack(side="left")
        ttk.Entry(fila_rango, textvariable=self.var_desde, width=12).pack(side="left", padx=(6, 10))
        ttk.Label(fila_rango, text="Hasta").pack(side="left")
        ttk.Entry(fila_rango, textvariable=self.var_hasta, width=12).pack(side="left", padx=(6, 10))
        BotonDegradado(fila_rango, text="Consultar rango", command=self.consultar_rango).pack(side="left")
        self.var_resultado_rango = tk.StringVar(value="Elige las fechas y presiona Consultar rango.")
        ttk.Label(self, textvariable=self.var_resultado_rango, wraplength=820, justify="left", foreground=TEXTO_SUAVE).pack(anchor="w", pady=(6, 0))

    @con_errores
    def consultar(self):
        periodo = {"Día": "dia", "Semana": "semana", "Mes": "mes", "Año": "anio"}[self.cb_periodo.get()]
        resultado = Finanzas.obtener_ingresos_detallados(periodo)
        self.var_total.set(dinero(resultado["total_general"]))
        self.var_servicios.set(dinero(resultado["total_servicios"]))
        self.var_productos.set(dinero(resultado["total_productos"]))

    @con_errores
    def hacer_corte(self):
        fecha = validar_fecha(self.var_fecha_corte.get(), "La fecha del corte")
        resultado = Reporte.obtener_corte_caja_diario(fecha.isoformat())
        if resultado.get("error"):
            raise ErrorOperacion(f"No se pudo generar el corte: {resultado['error']}")
        self.var_total_corte.set(dinero(resultado["gran_total_del_dia"]))
        llenar_tabla(self.tabla_corte, [
            {"id": i, "metodo": fila["metodo_pago"], "total": fila["total_recaudado"], "tickets": fila["numero_tickets"]}
            for i, fila in enumerate(resultado["desglose_por_metodo"])
        ], claves=["id", "metodo", "total", "tickets"], formatos=[None, None, dinero, None])

    @con_errores
    def consultar_rango(self):
        desde = validar_fecha(self.var_desde.get(), "La fecha de inicio")
        hasta = validar_fecha(self.var_hasta.get(), "La fecha final")
        if hasta < desde:
            raise ValueError("La fecha final no puede ser anterior a la fecha de inicio.")
        resultado = Finanzas.obtener_ingresos_por_rango(desde.isoformat(), hasta.isoformat())
        if resultado is None:
            raise ErrorOperacion("No se pudo consultar el rango de fechas.")
        self.var_resultado_rango.set(
            f"Del {resultado['fecha_inicio']} al {resultado['fecha_fin']}: "
            f"{dinero(resultado['gran_total'])} en {resultado['cantidad_tickets']} ticket(s)."
        )

    def refrescar(self):
        self.consultar()
        self.hacer_corte()


# ----------------------------------------------------------------------
# Respaldos
# ----------------------------------------------------------------------
class PanelRespaldos(ttk.Frame):
    def __init__(self, padre):
        super().__init__(padre, padding=24)
        self.var_estado = tk.StringVar()
        ttk.Label(self, text="Respaldo de la base de datos", style="Encabezado.TLabel").pack(anchor="w")
        ttk.Label(
            self, justify="left", foreground=TEXTO_SUAVE, wraplength=820,
            text="Genera un archivo .sql con mysqldump dentro de la carpeta 'respaldo' del proyecto. "
                 "También puedes restaurar la base desde un respaldo anterior.",
        ).pack(anchor="w", pady=(6, 16))
        fila = ttk.Frame(self)
        fila.pack(anchor="w")
        BotonDegradado(fila, text="Crear respaldo ahora", command=self.crear).pack(side="left")
        ttk.Button(fila, text="Restaurar desde un archivo…", command=self.restaurar).pack(side="left", padx=8)
        ttk.Label(self, textvariable=self.var_estado, wraplength=820, justify="left").pack(anchor="w", pady=16)

    def refrescar(self):
        pass

    @con_errores
    def crear(self):
        self.var_estado.set("Generando respaldo…")
        self.update_idletasks()
        gestor = GestorRespaldos()
        if gestor.crear_respaldo():
            self.var_estado.set(f"Respaldo creado en: {gestor.carpeta_respaldo}")
        else:
            self.var_estado.set("No se pudo crear el respaldo. Revisa la terminal para ver el error exacto.")

    @con_errores
    def restaurar(self):
        ruta = filedialog.askopenfilename(title="Elige un respaldo", filetypes=[("Archivos SQL", "*.sql")])
        if not ruta:
            return
        if not messagebox.askyesno(
            "Confirmar restauración",
            "Esto reemplaza el contenido actual de la base de datos con el del respaldo elegido.\n"
            "No se puede deshacer. ¿Continuar?",
        ):
            return
        gestor = GestorRespaldos()
        if gestor.restaurar_respaldo(ruta):
            self.var_estado.set(f"Base de datos restaurada desde:\n{ruta}")
            messagebox.showinfo("Listo", "La base de datos se restauró. Cambia de pestaña para ver los datos actualizados.")
        else:
            self.var_estado.set("No se pudo restaurar. Revisa la terminal para ver el error exacto.")


# ----------------------------------------------------------------------
# Usuarios (solo visible para el Dueño)
# ----------------------------------------------------------------------
class PanelUsuarios(ttk.Frame):
    def __init__(self, padre, usuario_actual):
        super().__init__(padre, padding=14)
        self.usuario_actual = usuario_actual
        self.filas = {}
        self.usuario_elegido = None
        self.var_nombres = tk.StringVar()
        self.var_apellido1 = tk.StringVar()
        self.var_apellido2 = tk.StringVar()
        self.var_username = tk.StringVar()
        self.var_password = tk.StringVar()

        formulario = ttk.LabelFrame(self, text=" Cuenta de usuario ", padding=12)
        formulario.pack(fill="x")
        campos = [
            ("Nombre(s) *", self.var_nombres, 18), ("Apellido paterno *", self.var_apellido1, 18),
            ("Apellido materno", self.var_apellido2, 18), ("Usuario (username) *", self.var_username, 16),
        ]
        for i, (texto, var, ancho) in enumerate(campos):
            ttk.Label(formulario, text=texto).grid(row=0, column=i, sticky="w", padx=(0, 4))
            
            tipo_val = "letras" if "Nombre" in texto or "Apellido" in texto else "texto"
            EntradaValidada(formulario, tipo=tipo_val, textvariable=var, width=ancho).grid(row=1, column=i, sticky="w", padx=(0, 16), pady=(0, 10))
            
        ttk.Label(formulario, text="Contraseña").grid(row=0, column=4, sticky="w", padx=(0, 4))
        ttk.Entry(formulario, textvariable=self.var_password, width=16, show="*").grid(row=1, column=4, sticky="w", padx=(0, 16), pady=(0, 10))
        ttk.Label(formulario, text="Rol *").grid(row=0, column=5, sticky="w", padx=(0, 4))
        self.cb_rol = ttk.Combobox(formulario, values=["Dueño", "Recepcionista"], state="readonly", width=14)
        self.cb_rol.set("Recepcionista")
        self.cb_rol.grid(row=1, column=5, sticky="w", pady=(0, 10))

        botones = ttk.Frame(formulario)
        botones.grid(row=2, column=0, columnspan=6, sticky="w")
        BotonDegradado(botones, text="Crear usuario", command=self.registrar).pack(side="left")
        ttk.Button(botones, text="Guardar cambios del elegido", command=self.guardar_cambios).pack(side="left", padx=6)
        ttk.Button(botones, text="Activar", command=self.activar).pack(side="left")
        ttk.Button(botones, text="Desactivar", command=self.desactivar).pack(side="left", padx=6)
        ttk.Button(botones, text="Eliminar por error", command=self.eliminar_por_error).pack(side="left")
        ttk.Button(botones, text="Limpiar", command=self.limpiar).pack(side="left", padx=6)
        ttk.Label(
            formulario, foreground=TEXTO_SUAVE, wraplength=760, justify="left",
            text="Para cambiar la contraseña del usuario elegido, escríbela y guarda los cambios. "
                 "Si dejas el campo en blanco, se conservará la contraseña que ya tenía el usuario.",
        ).grid(row=3, column=0, columnspan=6, sticky="w", pady=(6, 0))

        contenedor, self.tabla = crear_tabla(self, [
            ("id", "ID", 0, "w"), ("nombre", "Nombre", 220, "w"), ("usuario", "Usuario", 140, "w"),
            ("rol", "Rol", 120, "w"), ("estado", "Estado", 90, "w"), ("ultimo_acceso", "Último acceso", 160, "w"),
        ], altura=8)
        contenedor.pack(fill="both", expand=True, pady=(14, 0))
        self.tabla.bind("<<TreeviewSelect>>", self.al_seleccionar)

    def _comprobar_unico_dueno(self, id_usuario_afectado):
        """Retorna True si el usuario proporcionado es el ÚNICO Dueño activo en el sistema."""
        duenos_activos = [u for u in self.filas.values() if u.get("rol") == "Dueño" and u.get("estado") == "Activo"]
        if len(duenos_activos) <= 1:
            for u in duenos_activos:
                if u["id_usuario"] == id_usuario_afectado:
                    return True
        return False

    @con_errores
    def refrescar(self):
        filas = Usuario.obtener_todos_los_usuarios()
        for f in filas:
            f["nombre"] = nombre_completo(f)
            f["estado"] = "Activo" if f.get("activo") else "Inactivo"
        self.filas = llenar_tabla(self.tabla, filas, claves=["id_usuario", "nombre", "username", "rol", "estado", "ultimo_acceso"])

    def al_seleccionar(self, _evento=None):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        fila = self.filas[seleccion[0]]
        self.usuario_elegido = fila
        self.var_nombres.set(fila.get("nombres", ""))
        self.var_apellido1.set(fila.get("primer_apellido", ""))
        self.var_apellido2.set(fila.get("segundo_apellido") or "")
        self.var_username.set(fila.get("username", ""))
        self.var_password.set("")
        self.cb_rol.set(fila.get("rol", "Recepcionista"))

    @con_errores
    def registrar(self):
        nombres = convertir(self.var_nombres.get(), "texto", "Nombre(s)", True, 50)
        apellido1 = convertir(self.var_apellido1.get(), "texto", "Apellido paterno", True, 50)
        apellido2 = convertir(self.var_apellido2.get(), "texto", "Apellido materno", False, 50)
        username = convertir(self.var_username.get(), "texto", "Usuario", True, 50)
        password = convertir(self.var_password.get(), "texto", "Contraseña", True, 100)
        rol = self.cb_rol.get()
        if not Usuario.registrar_usuario(nombres, apellido1, apellido2, username, password, rol):
            raise ErrorOperacion("No se pudo crear la cuenta (revisa que el usuario no esté repetido).")
        self.limpiar()
        self.refrescar()

    @con_errores
    def guardar_cambios(self):
        if not self.usuario_elegido:
            raise ValueError("Elige un usuario de la tabla para editarlo.")
            
        nombres = convertir(self.var_nombres.get(), "texto", "Nombre(s)", True, 50)
        apellido1 = convertir(self.var_apellido1.get(), "texto", "Apellido paterno", True, 50)
        apellido2 = convertir(self.var_apellido2.get(), "texto", "Apellido materno", False, 50)
        username = convertir(self.var_username.get(), "texto", "Usuario", True, 50)
        password = self.var_password.get().strip()
        rol = self.cb_rol.get()

        if password and len(password) > 100:
            raise ValueError("La nueva contraseña no puede pasar de 100 caracteres.")

        if self.usuario_elegido["rol"] == "Dueño" and rol != "Dueño":
            if self._comprobar_unico_dueno(self.usuario_elegido["id_usuario"]):
                raise ValueError("No puedes quitarle el rol de Dueño a esta persona porque es el último administrador activo en el sistema.")

        if not Usuario.editar_usuario(self.usuario_elegido["id_usuario"], nombres, apellido1, apellido2, rol):
            raise ErrorOperacion("No se pudieron guardar los cambios básicos.")

        try:
            conexion = ConexionDB().conectar()
            cursor = conexion.cursor()
            
            cursor.execute("SELECT id_usuario FROM usuarios WHERE username = %s AND id_usuario != %s", 
                           (username, self.usuario_elegido["id_usuario"]))
            if cursor.fetchone():
                raise ValueError("Ese nombre de usuario ya lo está ocupando otra persona.")
            
            if password:
                cursor.execute("UPDATE usuarios SET username = %s, password = %s WHERE id_usuario = %s",
                               (username, password, self.usuario_elegido["id_usuario"]))
            else:
                cursor.execute("UPDATE usuarios SET username = %s WHERE id_usuario = %s",
                               (username, self.usuario_elegido["id_usuario"]))
            conexion.commit()
        except mysql.connector.Error as e:
            raise ErrorOperacion(f"Ocurrió un error al actualizar las credenciales: {e}")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()
                
        self.limpiar()
        self.refrescar()

    @con_errores
    def activar(self):
        id_usuario = seleccionado(self.tabla, "Elige un usuario de la tabla para activarlo.")
        if id_usuario is None:
            return
        Usuario.cambiar_estado(int(id_usuario), True)
        self.refrescar()

    @con_errores
    def desactivar(self):
        id_usuario = seleccionado(self.tabla, "Elige un usuario de la tabla para desactivarlo.")
        if id_usuario is None:
            return
        if int(id_usuario) == self.usuario_actual["id_usuario"]:
            raise ValueError("No puedes desactivar tu propia cuenta mientras tienes la sesión abierta.")
            
        if self._comprobar_unico_dueno(int(id_usuario)):
            raise ValueError("No puedes desactivar a este usuario porque el sistema se quedaría sin administradores (Dueños) activos.")
            
        if not messagebox.askyesno("Confirmar", "¿Desactivar esta cuenta? Ya no podrá iniciar sesión."):
            return
        Usuario.cambiar_estado(int(id_usuario), False)
        self.refrescar()

    @con_errores
    def eliminar_por_error(self):
        id_usuario = seleccionado(self.tabla, "Elige un usuario de la tabla para eliminarlo.")
        if id_usuario is None:
            return
        if int(id_usuario) == self.usuario_actual["id_usuario"]:
            raise ValueError("No puedes eliminar tu propia cuenta mientras tienes la sesión abierta.")
            
        if self._comprobar_unico_dueno(int(id_usuario)):
            raise ValueError("No puedes eliminar a este usuario porque el sistema se quedaría sin administradores (Dueños) activos.")
            
        if not messagebox.askyesno(
            "Confirmar",
            "Esto borra la cuenta por completo. Solo funciona si esa persona nunca ha cobrado un "
            "ticket de venta; si ya operó la caja, usa \"Desactivar\" en su lugar. ¿Continuar?",
        ):
            return
        if not Usuario.eliminar_usuario_por_error(int(id_usuario)):
            raise ErrorOperacion("No se pudo eliminar (es el administrador principal o ya tiene ventas registradas).")
        self.limpiar()
        self.refrescar()

    def limpiar(self):
        for var in (self.var_nombres, self.var_apellido1, self.var_apellido2, self.var_username, self.var_password):
            var.set("")
        self.cb_rol.set("Recepcionista")
        self.usuario_elegido = None
        self.tabla.selection_remove(*self.tabla.selection())


# ----------------------------------------------------------------------
# Ventana principal
# ----------------------------------------------------------------------
class Aplicacion(tk.Tk):
    def __init__(self, usuario_actual):
        super().__init__()
        self.usuario_actual = usuario_actual
        self.title("Barbería · Sistema de gestión")
        self.geometry("1220x820")
        self.minsize(1080, 720)
        self.configure(bg=FONDO)
        aplicar_estilos(self)
        
        self.protocol("WM_DELETE_WINDOW", self.confirmar_salida)

        # Carga del logo personalizado
        try:
            ruta_png = os.path.join(os.path.dirname(__file__), "logo.png")
            ruta_ico = os.path.join(os.path.dirname(__file__), "logo.ico")
            if os.path.exists(ruta_png):
                self.imagen_logo = tk.PhotoImage(file=ruta_png)
                self.iconphoto(True, self.imagen_logo)
            elif os.path.exists(ruta_ico):
                self.iconbitmap(ruta_ico)
        except Exception:
            pass

        encabezado = EncabezadoDegradado(
            self, "Barbería", f"Sesión: {nombre_completo(usuario_actual)} · {usuario_actual['rol']}",
        )
        encabezado.pack(fill="x")
        BandaBarbero(self).pack(fill="x")

        pie_pagina = ttk.Frame(self)
        pie_pagina.pack(side="bottom", fill="x", padx=12, pady=8)
        
        BotonDegradado(
            pie_pagina, 
            text="Cerrar sesión", 
            color_izq="#5b6577",
            color_der="#1b2333", 
            command=self.cerrar_sesion
        ).pack(side="right")

        self.cuaderno = ttk.Notebook(self)
        self.cuaderno.pack(fill="both", expand=True, padx=12, pady=(12, 0))

        paneles = [
            ("Citas", PanelCitas(self.cuaderno)),
            ("Ventas", PanelVentas(self.cuaderno, usuario_actual)),
            ("Clientes", PanelClientes(self.cuaderno)),
            ("Empleados", PanelEmpleados(self.cuaderno)),
            ("Servicios", PanelServicios(self.cuaderno)),
            ("Productos", PanelProductos(self.cuaderno)),
            ("Finanzas", PanelFinanzas(self.cuaderno)),
        ]
        
        if usuario_actual["rol"] == "Dueño":
            paneles.append(("Respaldos", PanelRespaldos(self.cuaderno)))
            paneles.append(("Usuarios", PanelUsuarios(self.cuaderno, usuario_actual)))
            
        for texto, panel in paneles:
            self.cuaderno.add(panel, text=texto)

        self.cuaderno.bind("<<NotebookTabChanged>>", self._al_cambiar_pestana)
        self.after(50, self._refrescar_actual)

    def _refrescar_actual(self):
        panel = self.nametowidget(self.cuaderno.select())
        if hasattr(panel, "refrescar"):
            panel.refrescar()

    def _al_cambiar_pestana(self, _evento=None):
        self._refrescar_actual()
        
    def confirmar_salida(self):
        if messagebox.askyesno("Salir del sistema", "¿Estás seguro que deseas cerrar el sistema de la Barbería?\n\nSi estás haciendo una venta y no la has cobrado, se perderán los datos del ticket actual."):
            self.destroy()

    def cerrar_sesion(self):
        if messagebox.askyesno("Cerrar sesión", "¿Estás seguro que deseas cerrar la sesión actual?"):
            self.destroy()
            main()

def main():
    try:
        conexion = ConexionDB().conectar()
    except mysql.connector.Error as e:
        conexion = None
        error = e
    else:
        error = None

    if conexion is None:
        raiz = tk.Tk()
        raiz.withdraw()
        if error is not None and error.errno == 1049:
            messagebox.showerror(
                "Error Crítico de Sistema",
                "La base de datos del sistema ('barberia_bd') no fue encontrada o no está inicializada.\n\n"
                "Por favor, contacte a su administrador de sistemas o soporte técnico para la instalación inicial."
            )
        else:
            messagebox.showerror(
                "No se pudo iniciar",
                "No se pudo conectar con MySQL.\n"
                "Revisa que el servidor esté encendido y que los datos de config.py sean correctos.\n\n"
                f"{error if error else ''}",
            )
        return
    conexion.close()

    login = VentanaLogin()
    login.mainloop()
    if login.usuario_autenticado:
        Aplicacion(login.usuario_autenticado).mainloop()


if __name__ == "__main__":
    main()