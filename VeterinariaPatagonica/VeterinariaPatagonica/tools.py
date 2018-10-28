#Este archivo tools se puede utilizar en todos los modelos que tienen baja logica
#Sirve para realizar los filtros en los modelos
#Trabaja con QuerySet

from django.db.models import Q
from django.db import models

#Esta clase sirve para gestionar las bajas
class BajasLogicasQuerySet(models.QuerySet):
    def habilitados(self):
        return self.filter(baja=False)

    def deshabilitados(self):
        return self.filter(baja=True)

#Esta funcion toma el diccionario (MAPPER) y retorna el objeto Q
def paramsToFilter(params, Modelo):
    mapper = getattr(Modelo, "MAPPER", {})
    filters = Q()
    for item in params.items():
        key = item[0]
        value = item[1]
        if key in mapper and value:
            name = mapper[key]
            filters &= name(value) if callable(name) else Q(**{name: value})
    return filters