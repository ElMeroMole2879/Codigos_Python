acceso_bd = {
    "host": "localhost",
    "user": "admin_barberia",
    "password": "Barberia2026*",
    "database": "barberia_bd",
    "port": 3306
}

GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP ON `barberia_bd%`.* TO 'admin_barberia'@'localhost';

El comodin % dice dale permiso sobre cualquier base de datos que empiece con la palabra 'barberia_bd'

cursor.execute(f"CREATE DATABASE {nombre_bd} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")

utf8mb4 = Guarda bien las letras ñ

unicode = regla internacional para ordenar palabras

_ci = Case Insensitive (Insensible a mayus y minus)

