from enum import Enum

__all__ =  [ "Areas" ]


class Area:
    def __init__(self, nombre, nombrePlural):
        self._nombre=nombre
        self._nombrePlural=nombrePlural

    def nombre(self):
        return self._nombre

    def nombrePlural(self):
        return self._nombrePlural


class Areas(Enum):

    C=Area("consulta", "consultas")
    Q=Area("cirugia", "cirugias")

    def codigos():
        return [ area.codigo() for area in Areas ]

    def nombres():
        return [ area.nombre() for area in Areas ]

    def nombresPlurales():
        return [ area.nombrePlural() for area in Areas ]

    def codificar(nombre):
        for area in Areas:
            if area.nombre() == nombre or area.nombrePlural() == nombre:
                return area.codigo()

    def paresOrdenados():
        return [
            (area.codigo(), area.nombre().capitalize()) for area in Areas
        ]

    def codigo(self):
        return self.name

    def nombre(self):
        return self.value.nombre()

    def nombrePlural(self):
        return self.value.nombrePlural()
