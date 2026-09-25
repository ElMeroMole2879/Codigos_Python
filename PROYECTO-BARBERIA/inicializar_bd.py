import mysql.connector
from mysql.connector import Error
from config import acceso_bd

class InicializadorBD:
    def __init__(self):
        self.credenciales = acceso_bd

    def configurar_base_datos(self):
        try:
            conexion = mysql.connector.connect(
                host=self.credenciales["host"],
                user=self.credenciales["user"],
                password=self.credenciales["password"],
                port=self.credenciales["port"]
            )
            
            if conexion.is_connected():
                cursor = conexion.cursor()
                nombre_bd = self.credenciales["database"]

                print(f"Preparando arquitectura para: {nombre_bd}...")
                cursor.execute(f"DROP DATABASE IF EXISTS {nombre_bd};")
                cursor.execute(f"CREATE DATABASE {nombre_bd} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
                cursor.execute(f"USE {nombre_bd};")

                # TABLA 1: Usuarios (Login y Seguridad)
                cursor.execute("""
                CREATE TABLE Usuarios (
                    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
                    nombres VARCHAR(50) NOT NULL,
                    primer_apellido VARCHAR(50) NOT NULL,
                    segundo_apellido VARCHAR(50),
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    rol ENUM('Dueño', 'Recepcionista') NOT NULL,
                    activo BOOLEAN DEFAULT TRUE,
                    ultimo_acceso DATETIME NULL
                );
                """)

                # TABLA 2: Empleados (Con sistema de nómina y comisiones)
                cursor.execute("""
                CREATE TABLE Empleados (
                    id_empleado INT AUTO_INCREMENT PRIMARY KEY,
                    nombres VARCHAR(50) NOT NULL,
                    primer_apellido VARCHAR(50) NOT NULL,
                    segundo_apellido VARCHAR(50),
                    curp VARCHAR(18) UNIQUE NOT NULL,
                    telefono VARCHAR(15) UNIQUE NOT NULL,
                    correo VARCHAR(100) UNIQUE,
                    calle VARCHAR(100) NOT NULL,
                    num_exterior VARCHAR(10) NOT NULL,
                    num_interior VARCHAR(10),
                    colonia VARCHAR(100) NOT NULL,
                    cp VARCHAR(5) NOT NULL,
                    puesto VARCHAR(50) NOT NULL,
                    salario_base DECIMAL(10, 2) DEFAULT 0.00,
                    porcentaje_comision DECIMAL(5, 2) DEFAULT 0.00,
                    activo BOOLEAN DEFAULT TRUE
                );
                """)

                # TABLA 3: Clientes (Con preferencias de corte)
                cursor.execute("""
                CREATE TABLE Clientes (
                    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
                    nombres VARCHAR(50) NOT NULL,
                    primer_apellido VARCHAR(50) NOT NULL,
                    segundo_apellido VARCHAR(50),
                    telefono VARCHAR(15) UNIQUE NOT NULL,
                    corte_preferido VARCHAR(100)
                );
                """)

                # TABLA 4: Servicios
                cursor.execute("""
                CREATE TABLE Servicios (
                    id_servicio INT AUTO_INCREMENT PRIMARY KEY,
                    nombre_servicio VARCHAR(100) NOT NULL,
                    precio_actual DECIMAL(10, 2) NOT NULL,
                    duracion_minutos INT NOT NULL
                );
                """)

                # TABLA 5: Productos
                cursor.execute("""
                CREATE TABLE Productos (
                    id_producto INT AUTO_INCREMENT PRIMARY KEY,
                    nombre_producto VARCHAR(100) NOT NULL,
                    marca VARCHAR(50) NOT NULL,
                    precio_venta_actual DECIMAL(10, 2) NOT NULL,
                    stock_total INT DEFAULT 0
                );
                """)

                # TABLA 6: Entradas de Inventario
                cursor.execute("""
                CREATE TABLE Entradas_Inventario (
                    id_entrada INT AUTO_INCREMENT PRIMARY KEY,
                    id_producto INT NOT NULL,
                    fecha_llegada DATE NOT NULL,
                    cantidad INT NOT NULL,
                    costo_unitario DECIMAL(10, 2) NOT NULL,
                    fecha_caducidad DATE,
                    FOREIGN KEY (id_producto) REFERENCES Productos(id_producto) ON DELETE RESTRICT
                );
                """)

                # TABLA 7: Citas
                cursor.execute("""
                CREATE TABLE Citas (
                    id_cita INT AUTO_INCREMENT PRIMARY KEY,
                    id_cliente INT NOT NULL,
                    id_empleado INT NOT NULL, 
                    id_servicio INT NOT NULL,
                    fecha_cita DATE NOT NULL,
                    hora_cita TIME NOT NULL,
                    estado ENUM('Pendiente', 'Completada', 'Cancelada') DEFAULT 'Pendiente',
                    FOREIGN KEY (id_cliente) REFERENCES Clientes(id_cliente) ON DELETE CASCADE,
                    FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado) ON DELETE RESTRICT,
                    FOREIGN KEY (id_servicio) REFERENCES Servicios(id_servicio) ON DELETE RESTRICT
                );
                """)

                # TABLA 8: Notas del Historial del Cliente
                cursor.execute("""
                CREATE TABLE Notas_Historial_Cliente (
                    id_nota INT AUTO_INCREMENT PRIMARY KEY,
                    id_cliente INT NOT NULL,
                    id_empleado INT NOT NULL, 
                    fecha_nota DATE NOT NULL,
                    descripcion TEXT NOT NULL,
                    FOREIGN KEY (id_cliente) REFERENCES Clientes(id_cliente) ON DELETE CASCADE,
                    FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado) ON DELETE RESTRICT
                );
                """)

                # TABLA 9: Ventas (Ticket principal)
                cursor.execute("""
                CREATE TABLE Ventas (
                    id_venta INT AUTO_INCREMENT PRIMARY KEY,
                    id_cliente INT, 
                    id_usuario INT NOT NULL, 
                    fecha_hora DATETIME NOT NULL,
                    total DECIMAL(10, 2) NOT NULL,
                    metodo_pago ENUM('Efectivo', 'Tarjeta', 'Transferencia') NOT NULL,
                    FOREIGN KEY (id_cliente) REFERENCES Clientes(id_cliente) ON DELETE SET NULL,
                    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE RESTRICT
                );
                """)

                # TABLA 10: Detalle de Venta - Servicios (Para comisiones)
                cursor.execute("""
                CREATE TABLE Detalle_Venta_Servicios (
                    id_detalle_servicio INT AUTO_INCREMENT PRIMARY KEY,
                    id_venta INT NOT NULL,
                    id_servicio INT NOT NULL,
                    id_empleado INT NOT NULL, 
                    precio_cobrado DECIMAL(10, 2) NOT NULL, 
                    FOREIGN KEY (id_venta) REFERENCES Ventas(id_venta) ON DELETE CASCADE,
                    FOREIGN KEY (id_servicio) REFERENCES Servicios(id_servicio) ON DELETE RESTRICT,
                    FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado) ON DELETE RESTRICT
                );
                """)

                # TABLA 11: Detalle de Venta - Productos (Para descontar stock)
                cursor.execute("""
                CREATE TABLE Detalle_Venta_Productos (
                    id_detalle_producto INT AUTO_INCREMENT PRIMARY KEY,
                    id_venta INT NOT NULL,
                    id_producto INT NOT NULL,
                    cantidad INT NOT NULL,
                    precio_cobrado DECIMAL(10, 2) NOT NULL,
                    FOREIGN KEY (id_venta) REFERENCES Ventas(id_venta) ON DELETE CASCADE,
                    FOREIGN KEY (id_producto) REFERENCES Productos(id_producto) ON DELETE RESTRICT
                );
                """)

                # Inserción del usuario administrador por defecto
                # Si no se hace esto, no habrá forma de entrar al sistema la primera vez.
                cursor.execute("""
                INSERT INTO Usuarios (nombres, primer_apellido, username, password, rol) 
                VALUES ('Admin', 'Sistema', 'admin', '12345', 'Dueño');
                """)

                conexion.commit()
                print("Base de datos y tablas creadas exitosamente. Usuario administrador 'admin' con contraseña '12345'.")
                
        except Error as e:
            print(f"Error al configurar la base de datos: {e}")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

if __name__ == "__main__":
    app = InicializadorBD()
    app.configurar_base_datos()