from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):

    def permitidos(self, choices):

        if self.is_superuser:
            return tuple(choices)

        permisos = self.get_all_permissions()
        seleccionados = []

        for item in choices:
            permiso = "GestionDePracticas.add_"+item[0]
            if permiso in permisos:
                seleccionados.append(item)

        return tuple(seleccionados)
