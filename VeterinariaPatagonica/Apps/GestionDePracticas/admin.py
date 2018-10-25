from django.contrib import admin
from .models import *

class PracticaServicioInline(admin.TabularInline):
    model = PracticaServicio

class PracticaAdmin(admin.ModelAdmin):
    inlines = [
        PracticaServicioInline,
    ]

class PracticaInsumoInline(admin.TabularInline):
    model = PracticaProducto


admin.site.register(Practica, PracticaAdmin)
