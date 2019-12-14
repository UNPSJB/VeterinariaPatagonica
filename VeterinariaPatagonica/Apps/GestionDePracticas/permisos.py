from django.db.models import Q

from django.db.models import Max

from VeterinariaPatagonica.areas import Areas
from VeterinariaPatagonica.tools import R
from Apps.GestionDePracticas.models import Practica, Estado


__all__ = ("paraPractica", "enArea", "paraCrear", "filtroPermitidas")



def paraPractica(usuario, acciones, practica, estado=None):
    retorno = True

    area = practica.nombreTipo()
    estado = practica.estado() if estado is None else estado
    encargado = "atendida" if estado.usuario == usuario else "no_atendida"

    retorno = enArea(
        usuario,
        acciones,
        area,
        estado=estado,
        encargado=encargado
    )

    return retorno



def enArea(usuario, acciones, area, estado=None, encargado="atendida"):

    retorno = True

    if type(acciones) != list:
        acciones = [acciones]

    if type(estado) != str:
        if isinstance(estado, Estado):
            estado = estado.nombre()
        elif issubclass(estado, Estado):
            estado = estado.__name__.lower()
        else:
            estado = ""

    if isinstance(area, Areas):
        area = area.nombre()
    elif type(area) != str:
        area = ""

    for accion in acciones:
        cualquier_estado = usuario.has_perm("GestionDePracticas.%s_%s_%s" % (
            accion.name,
            area,
            encargado
        ))

        estado_particular = usuario.has_perm("GestionDePracticas.%s_%s_%s_%s" % (
            accion.name,
            area,
            estado,
            encargado,
        )) if estado is not None else False

        if not (estado_particular or cualquier_estado):
            retorno = False
            break

    return retorno



def paraCrear(usuario, area, accion=None):

    retorno = usuario.has_perm("GestionDePracticas.%s_%s_atendida" % (
        Practica.Acciones.crear.name,
        area.nombre()
    ))

    if accion is not None:
        retorno &= enArea(
            usuario,
            accion,
            area,
            estado="creada"
        )

    return retorno



def filtroPermitidas(usuario, accion, encargados=None, areas=None, estados=None):
    retorno = []

    areas = [areas] if (areas is not None) and (type(areas) != list) else areas
    areas = Areas if (areas is None) else areas
    areas = { area.codigo() : area.nombre() for area in areas }

    if estados is None:
        estados = { dupla[0]:dupla[1] for dupla in Estado.TIPOS }
    else:
        estados = [estados] if type(estados) != list else estados
        estados = { estado.TIPO : estado.__name__.lower() for estado in estados }

    encargados = ("atendida", "no_atendida") if encargados is None else encargados
    encargados = { (usuario.id if encargado=="atendida" else -usuario.id) : encargado for encargado in encargados }

    for valor_area,area in areas.items():
        for valor_encargado,encargado in encargados.items():

            q = [ Q(id_atendida_por=abs(valor_encargado)), Q(tipo=valor_area) ]
            q[0] = ~q[0] if encargado == "no_atendida" else q[0]

            permiso = "GestionDePracticas.%s_%s_%s" % (accion.name,area,encargado)
            if usuario.has_perm(permiso):
                retorno.append( Q(*q) )

            else:
                valores_estado = []
                for valor_estado,estado in estados.items():

                    permiso = "GestionDePracticas.%s_%s_%s_%s" % (accion.name,area,estado,encargado)
                    if usuario.has_perm(permiso):
                        valores_estado.append(valor_estado)

                if len(valores_estado):
                    q = q + [Q(tipo_estado_actual__in=valores_estado)]
                    retorno.append(Q(*q))

    return R(*retorno) if len(retorno) else None



def permitidas(usuario, accion, practicas):

    return [
        practica.id for practica in practicas if paraPractica(usuario, accion, practica)
    ]
