from enum import Enum

__all__ =  [ "Areas" ]



class Area:
    def __init__(self, nombre, nombrePlural):
        self._nombre=nombre
        self._nombrePlural=nombrePlural
    @property
    def nombre(self):
        return self._nombre
    @property
    def nombrePlural(self):
        return self._nombrePlural



class Areas(Enum):

    C=Area("consulta", "consultas")
    Q=Area("cirugia", "cirugias")
    I=Area("internacion", "internaciones")

    @classmethod
    def practica(cls):
        return tuple( [ (area.codigo, area.nombre) for area in [C,Q] ] )

    @classmethod
    def codigos(cls):
        return tuple( [ area.name for area in cls ] )

    @classmethod
    def nombres(cls):
        return tuple( [ area.nombre for area in cls ] )

    @classmethod
    def nombresPlurales(cls):
        return tuple( [ area.nombrePlural for area in cls ] )

    @classmethod
    def codificar(cls, nombre):
        for area in cls:
            if area.nombre == nombre or area.nombrePlural == nombre:
                return area.codigo

    @classmethod
    def choices(cls):
        return tuple([
            (area.codigo, area.nombre.capitalize()) for area in cls
        ])

    @classmethod
    def caracteresCodigo(cls):
        return 1

    @property
    def codigo(self):
        return self.name

    @property
    def nombre(self):
        return self.value.nombre

    @property
    def nombrePlural(self):
        return self.value.nombrePlural
