"""
    Si transicionamos una practica, aunque no cambie ningun atributo del
    modelo Practica, estariamos cambiando la practica? Seria la idea
    usar los permisos por defecto para cosas asi, o, son para tomarselos
    mas literal respecto a las entidades del modelo ER?
    Seria bueno hacer decorators como el permission_required? no parece necesario.
    Creo que tendriamos que crear permisos para cada accion que los
    requiera y asignarselos a grupos. Para algunos reportes/listados van a ser
    necesarios porque Django crea permisos add/change/delete

"""

PERMISOS_DETALLES = [
    'GestionDePracticas.change_practica',
    'GestionDePracticas.change_realizada',
    'GestionDePracticas.add_realizadaservicio',
    'GestionDePracticas.change_realizadaservicio',
    'GestionDePracticas.delete_realizadaservicio',
    'GestionDePracticas.add_realizadaproducto',
    'GestionDePracticas.change_realizadaproducto',
    'GestionDePracticas.delete_realizadaproducto',
]
PERMISOS_CREAR = [
    'GestionDePracticas.add_creada',
    'GestionDePracticas.add_practica',
    'GestionDePracticas.add_practicaservicio',
    'GestionDePracticas.add_practicaproducto',
]
PERMISOS_PRESUPUESTAR = [
    'GestionDePracticas.change_practica',
    'GestionDePracticas.add_presupuestada',
]
PERMISOS_PROGRAMAR = [
    'GestionDePracticas.change_practica',
    'GestionDePracticas.add_programada',
]
PERMISOS_REALIZAR = [
    'GestionDePracticas.change_practica',
    'GestionDePracticas.add_realizada',
]
PERMISOS_CANCELAR = [
    'GestionDePracticas.change_practica',
    'GestionDePracticas.add_cancelada',
]