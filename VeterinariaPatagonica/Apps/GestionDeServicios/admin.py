from django.contrib import admin
from .models import Servicio
from .models import ServicioInsumo

class ServicioInsumoInline(admin.TabularInline):
    model = ServicioInsumo

class ServicioAdmin(admin.ModelAdmin):
    inlines = [
        ServicioInsumoInline,
    ]

admin.site.register(Servicio, ServicioAdmin)
