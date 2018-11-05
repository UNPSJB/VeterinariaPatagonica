from django.contrib import admin
from .models.practica import Practica, PracticaProducto, PracticaServicio

admin.site.register(Practica)
admin.site.register(PracticaProducto)
admin.site.register(PracticaServicio)
