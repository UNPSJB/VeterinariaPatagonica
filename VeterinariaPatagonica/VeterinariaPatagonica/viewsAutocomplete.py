from datetime import datetime

from django.http import HttpResponse
from django.contrib.auth.models import AnonymousUser

from VeterinariaPatagonica.tools import R
from Apps.GestionDeServicios.models import Servicio
from Apps.GestionDeProductos.models import Producto
from Apps.GestionDeClientes.models import Cliente
from Apps.GestionDeMascotas.models import Mascota
from Apps.GestionDePracticas import permisos
from Apps.GestionDePracticas.models import Practica, Estado, Realizada
from Apps.GestionDeTiposDeAtencion.models import TipoDeAtencion

from dal.autocomplete import Select2QuerySetView

from django.db.models import Count, Sum, Q, Value, When, Case, CharField



def servicioSelectLabel(servicio):
    retorno = servicio.nombre
    if servicio.descripcion:
        retorno = "%s: %s" % (servicio.nombre, servicio.descripcion)
    return retorno



def servicioSelectLabelActiva(servicio):
    return "%10s:  %s $%.2f  (%d min.)" % (
        servicio.get_tipo_display().capitalize(),
        servicio.nombre,
        servicio.precioTotal(),
        servicio.tiempoEstimado
    )



def productoSelectLabel(producto):
    retorno = "Producto" if producto.precioPorUnidad > 0 else "Insumo"
    retorno = "%s: %s - %s" % (retorno, producto.marca, producto.nombre)
    if producto.descripcion:
        retorno = "%s (%s)" % (retorno, producto.descripcion)
    return "%s en %s" % (retorno, producto.rubro.nombre)



def productoSelectLabelActiva(producto):
    nombre = producto.nombre
    compra = producto.precioDeCompra
    venta = producto.precioPorUnidad
    stock = producto.stock
    presentacion = producto.get_formaDePresentacion_display()
    if venta > 0:
        return "Producto:  %s X %s $%.2f  (%d en stock)" % (nombre, presentacion, venta, stock)
    else:
        return "Insumo:    %s X %s $%.2f  (%d en stock)" % (nombre, presentacion, compra, stock)



def tipoDeAtencionSelectLabel(tipoDeAtencion):

    validoAhora = tipoDeAtencion.esValido( datetime.now() )
    retorno = " (fuera de horario)" if not validoAhora else ""

    return "%s%s: %s" % (tipoDeAtencion.nombre, retorno, tipoDeAtencion.descripcion)



def tipoDeAtencionSelectLabelActiva(tipoDeAtencion):

    validoAhora = tipoDeAtencion.esValido( datetime.now() )
    retorno = " (fuera de horario)" if not validoAhora else ""

    lugar = tipoDeAtencion.get_lugar_display()
    tipo = tipoDeAtencion.get_tipoDeServicio_display()
    emergencia = ", Emergencia" if tipoDeAtencion.emergencia else ""

    return "%s%s, %%%.2f de recargo - %s, %s%s" % (
        tipoDeAtencion.nombre,
        retorno,
        tipoDeAtencion.recargo,
        lugar,
        tipo,
        emergencia
    )



def clienteSelectLabel(cliente):
    return "%s: %s %s (Cliente %s)" % (
        cliente.dniCuit,
        cliente.apellidos,
        cliente.nombres,
        cliente.get_tipoDeCliente_display()
    )



def mascotaSelectLabel(mascota):
    return "%s: %s (%s %s)" % (mascota.patente, mascota.nombre, mascota.especie, mascota.raza)



def practicaRealizadaSelectLabel(practica):
    return "%s: $%.2f\t(%s, realizada a '%s' de %s)" % (
        str(practica),
        practica.precio,
        practica.tipoDeAtencion.nombre,
        practica.mascota.nombre,
        str(practica.cliente)
    )



class Autocomplete(Select2QuerySetView):

    http_method_names = ('get',)
    permisos_necesarios = ()

    def estaAutorizado(self, usuario):
        return (
            not isinstance(usuario, AnonymousUser)
        ) and (
            usuario.has_perms(self.permisos_necesarios)
        )

    def dispatch(self, request, *args, **kwargs):
        response = None
        if self.estaAutorizado(request.user):
            response = super().dispatch(request, *args, **kwargs)
        else:
            response = HttpResponse()
            response.status_code = 403
        return response



class ServicioAutocomplete(Autocomplete):

    whens = [When( Q(tipo=tipo[0]), then=Value(tipo[1]) ) for tipo in Servicio.TIPO]
    areas = tuple(tipo[0] for tipo in Servicio.TIPO)
    area = None
    permisos_necesarios = (
        "GestionDeServicios.servicio_listar_habilitados",
        "GestionDeServicios.servicio_ver_habilitados"
    )

    def dispatch(self, request, area=None, *args, **kwargs):
        response = None
        if (area is None) or (area in self.areas):
            self.area = area
            response = super().dispatch(request, *args, **kwargs)
        else:
            response = HttpResponse()
            response.status_code = 404
        return response

    def get_queryset(self):
        queryset = Servicio.objects.habilitados()
        if self.area:
            queryset = queryset.filter(tipo=self.area)

        if self.q:
            query = {
                "nombre__icontains" : self.q,
                "descripcion__icontains" : self.q
            }

            if not self.area:
                queryset = queryset.annotate(
                    nombre_tipo=Case(
                        *self.whens,
                        output_field=CharField()
                    )
                )
                query["nombre_tipo__icontains"] = self.q

            queryset = queryset.filter(R(**query)).annotate(
                cuenta_practicas=Count("practica")
            ).order_by("-cuenta_practicas")

        return queryset

    def get_result_label(self, result):
        return servicioSelectLabel(result)

    def get_selected_result_label(self, result):
        return servicioSelectLabelActiva(result)



class ProductoAutocomplete(Autocomplete):

    tipos = ("insumos", "productos")
    tipo = None
    permisos_necesarios = (
        "GestionDeProductos.producto_listar_habilitados",
        "GestionDeProductos.producto_ver_habilitados"
    )

    def dispatch(self, request, tipo=None, *args, **kwargs):
        response = None
        if (tipo is None) or (tipo in self.tipos):
            self.tipo = tipo
            response = super().dispatch(request, *args, **kwargs)
        else:
            response = HttpResponse()
            response.status_code = 404
        return response

    def get_queryset(self):
        queryset = Producto.objects.habilitados()
        if self.tipo == "insumos":
            queryset = queryset.filter(precioPorUnidad=0)
        elif self.tipo == "productos":
            queryset = queryset.filter(precioPorUnidad__gt=0)
        if self.q:
            query = {
                "marca__icontains" : self.q,
                "nombre__icontains" : self.q,
                "descripcion__icontains" : self.q,
                "rubro__nombre__icontains" : self.q
            }
            if self.tipo is None:
                queryset = queryset.annotate(
                    nombre_tipo=Case(
                        When(Q(precioPorUnidad=0), then=Value("insumo")),
                        default=Value("producto"),
                        output_field=CharField()
                    )
                )
                query["nombre_tipo__icontains"] = self.q
            queryset = queryset.filter(R(**query)).annotate(
                cuenta_practicas=Count("practica")
            ).order_by("-cuenta_practicas")
        return queryset

    def get_result_label(self, result):
        return productoSelectLabel(result)

    def get_selected_result_label(self, result):
        return productoSelectLabelActiva(result)



class TipoDeAtencionAutocomplete(Autocomplete):

    permisos_necesarios = (
        "GestionDeTiposDeAtencion.tipodeatencion_listar_habilitados",
        "GestionDeTiposDeAtencion.tipodeatencion_ver_habilitados"
    )

    def get_queryset(self):
        queryset = TipoDeAtencion.objects.habilitados().validosPrimero()
        if self.q:
            queryset = queryset.filter(R(
                nombre__icontains=self.q,
                descripcion__icontains=self.q
            ))
        return queryset

    def get_result_label(self, result):
        return tipoDeAtencionSelectLabel(result)

    def get_selected_result_label(self, result):
        return tipoDeAtencionSelectLabelActiva(result)



class ClienteAutocomplete(Autocomplete):

    permisos_necesarios = (
        "GestionDeClientes.cliente_listar_habilitados",
        "GestionDeClientes.cliente_ver_habilitados"
    )

    def get_queryset(self):
        queryset = Cliente.objects.habilitados()
        if self.q:
            queryset = queryset.filter(R(
                dniCuit__icontains=self.q,
                nombres__icontains=self.q,
                apellidos__icontains=self.q
            ))
        return queryset

    def get_result_label(self, result):
        return clienteSelectLabel(result)



class MascotaAutocomplete(Autocomplete):

    cliente=None
    permisos_necesarios = (
        "GestionDeMascotas.mascota_listar_habilitados",
        "GestionDeMascotas.mascota_ver_habilitados"
    )

    def dispatch(self, request, cliente=None, *args, **kwargs):
        response = None
        valido = True
        if cliente is not None:
            valido = Cliente.objects.habilitados().filter(id=cliente).exists()
        if valido:
            self.cliente = cliente
            response = super().dispatch(request, *args, **kwargs)
        else:
            response = HttpResponse()
            response.status_code = 404
        return response

    def get_queryset(self):
        queryset = Mascota.objects.habilitados()
        if self.cliente is not None:
            queryset = queryset.filter(cliente__id=self.cliente)
        if self.q:
            queryset = queryset.filter(R(
                patente__icontains=self.q,
                nombre__icontains=self.q,
                especie__icontains=self.q,
                raza__icontains=self.q
            ))
        return queryset

    def get_result_label(self, result):
        return mascotaSelectLabel(result)



class PracticaRealizadaAutocomplete(Autocomplete):

    filtros=None

    def estaAutorizado(self, usuario):
        if isinstance(usuario, AnonymousUser):
            return False
        self.filtros = permisos.filtroPermitidas(
            usuario,
            Practica.Acciones.listar,
            estados=Realizada,
        )
        return (self.filtros is not None)

    def get_queryset(self):
        queryset = Practica.objects.none()
        cliente = self.forwarded["cliente"] if "cliente" in self.forwarded else None
        if cliente is not None:

            queryset = Practica.objects.enEstado(Realizada).filter(cliente__id=int(cliente))
            queryset = Estado.anotarPracticas(
                queryset,
                actualizada_por=True,
                estado_actual=True
            ).filter(self.filtros)

            if self.q:
                queryset = queryset.filter(R(
                    mascota__nombre__icontains=self.q,
                    mascota__patente__icontains=self.q,
                    tipoDeAtencion__nombre__icontains=self.q
                ))
        return queryset

    def get_result_label(self, result):
        return practicaRealizadaSelectLabel(result)
