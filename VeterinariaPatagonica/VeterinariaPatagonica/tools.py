#Este archivo tools se puede utilizar en todos los modelos que tienen baja logica
#Sirve para realizar los filtros en los modelos
#Trabaja con QuerySet

from django.db.models import Q
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from .errores import VeterinariaPatagonicaError

#from VeterinariaPatagonica.Apps.GestionDeProductos.models import Producto
from dal import autocomplete


class VeterinariaPatagonicaQuerySet(models.QuerySet):

    def get(self, **kwargs):
        try:
            object = super().get(**kwargs)
        except ObjectDoesNotExist:
            raise VeterinariaPatagonicaError(
                titulo="Objeto '%s' no encontrado" % self.model.__name__,
                descripcion="El objeto solicitado no fue encontrado",
            )
        return object


#Esta clase sirve para gestionar las bajas
class BajasLogicasQuerySet(VeterinariaPatagonicaQuerySet):
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


class R(models.Q):
    default=models.Q.OR


'''
class productoAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        qs = Producto.objects.all()

        if self.q:
           qs = qs.filter(Q(descripcion__icontains=self.q) | Q(nombre__icontains=self.q) | Q(marca__icontains=self.q))

        return qs


'''