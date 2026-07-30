import bd.base_datos as sqlbd

columnas = [
    {
        'name' : 'id',
        'type' : 'INT',
        'length' : 10,
        'primary_key' : True,
        'auto_increment' : True,
        'not_null' : True
    },
    {
        
        'name' : 'nombre',
        'type' : 'VARCHAR',
        'length' : 32,
        'primary_key' : False,
        'auto_increment' : False,
        'not_null' : True
    },
    {
        
        'name' : 'apellido',
        'type' : 'VARCHAR',
        'length' : 32,
        'primary_key' : False,
        'auto_increment' : False,
        'not_null' : True
    },
    {
        'name' : 'telefono',
        'type' : 'VARCHAR',
        'length' : 9,
        'primary_key' : False,
        'auto_increment' : False,
        'not_null' : True
    },
    {
        'name' : 'direccion',
        'type' : 'VARCHAR',
        'length' : 128,
        'primary_key' : False,
        'auto_increment' : False,
        'not_null' : True
    }
        ]