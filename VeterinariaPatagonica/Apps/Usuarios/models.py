from django.contrib.auth.models import AbstractUser

from Apps.GestionDePracticas.models.practica import Practica

class Usuario(AbstractUser):

    def acciones(self):

        acciones = set(Practica.Acciones)

        if self.is_superuser:
            return acciones

        seleccionados = set()
        permisos = self.get_all_permissions()

        for accion in acciones:
            if accion.idPermiso() in permisos:
                seleccionados.add(accion)

        return seleccionados
