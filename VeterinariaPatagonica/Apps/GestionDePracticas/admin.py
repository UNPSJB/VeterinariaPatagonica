from django.contrib import admin
from .models.practica import Practica, PracticaProducto, PracticaServicio, Adelanto
from .models.estado import Estado, Presupuestada, Programada, Realizada, Facturada, Cancelada

admin.site.register(Practica)
admin.site.register(PracticaProducto)
admin.site.register(PracticaServicio)
admin.site.register(Adelanto)
admin.site.register(Estado)
admin.site.register(Presupuestada)
admin.site.register(Programada)
admin.site.register(Realizada)
admin.site.register(Facturada)
admin.site.register(Cancelada)
