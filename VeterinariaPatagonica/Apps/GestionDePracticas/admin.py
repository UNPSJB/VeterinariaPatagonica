from django.contrib import admin
from .models import *

class PracticaServicioInline(admin.TabularInline):
    model = PracticaServicio

class PracticaAdmin(admin.ModelAdmin):
    inlines = [
        PracticaServicioInline,
    ]

class PracticaInsumoInlune(admin.TabularInline):
    model = PracticaInsumo


admin.site.register(Practica, PracticaAdmin)
