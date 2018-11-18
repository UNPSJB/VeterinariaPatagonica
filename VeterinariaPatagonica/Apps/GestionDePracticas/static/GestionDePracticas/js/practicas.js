function eliminar(e, formsetdiv){

    e.preventDefault();

    if ($(formsetdiv+" .formset-form.habilitado").length < 2)
        return;

    var div = $(e.target).parents(".formset-form.habilitado").first();
    var pos = div.index();
    var prefix = formsetdiv.slice(5);

    if ( existente(div.get(0), prefix, pos) )
        ocultarEliminado(div, prefix, pos)
    else
        eliminarNuevo(div, prefix, pos);
}

function existente(div, prefix, pos){

    var id = ["id_"+prefix, pos, "id"].join("-");
    return document.getElementById(id).value != "";
}

function agregar(formsetdiv){

    var todos = $(formsetdiv+' .formset-form');
    var habilitados = $(formsetdiv+' .formset-form.habilitado');
    var prefix = formsetdiv.slice(5);
    var nuevo = $("#empty-form-"+prefix).children().first().clone();
    var nuevo_id = todos.length;
    var nuevo_posicion = todos.length + 1;

    inicializar(nuevo, nuevo_id, nuevo_posicion);
    todos.last().after(nuevo);
    actualizarTotal(prefix, nuevo_posicion);
}

function cambiarId(item, prefix, id){

    var inputs = item.find("input, textarea, select")
    for (i=0 ; i<(inputs.length) ; i++){

        input = inputs.get(i)

        campo = input.name.split("-")[2]
        nombre = [prefix, id, campo].join("-")
        input.id = "id_" + nombre
        input.name = nombre
    }

    var labels = item.find("label")
    for (i=0 ; i<(labels.length) ; i++){

        label = labels.get(i)

        campo = $(label).attr("for").split("-")[2]
        para = ["id_"+prefix, id, campo].join("-")
        $(label).attr("for", para)
    }
}

function inicializar(item, id, order){

    var i, input, value;
    var inputs = item.find("input, textarea, select");

    for (i=0 ; i<(inputs.length) ; i++){

        input = $(inputs.get(i));

        value = input.attr("id")
        if ( value )
            input.attr("id", value.replace("__prefix__", id));

        value = input.attr("for")
        if ( value )
            input.attr("for", value.replace("__prefix__", id));

        value = input.attr("name")
        if ( value )
            input.attr("name", value.replace("__prefix__", id));
    }

    item.find(".form-group.ORDER input[type=hidden]").first().attr("value", order);
}

function ocultarEliminado(div, prefix, pos){

    div.removeClass("habilitado");
    div.addClass("deshabilitado");
    div.addClass("hidden");

    var id_str = ["id_"+prefix, pos, "DELETE"].join("-");
    document.getElementById(id_str).value = "true";
}

function eliminarNuevo(div, prefix, pos){

    var sig = div.next();
    
    $(div).remove();
    
    while (sig.index() != -1) {
        cambiarId(sig, prefix, pos);
        pos++;
        sig = sig.next();
    }

    actualizarTotal(prefix, pos);
}

function actualizarTotal(prefix, cantidad){

    $('input#id_'+prefix+'-TOTAL_FORMS').attr('value',cantidad);
}

function compararServicios(unForm, otroForm){

    var unSelect    = unForm.find(".servicio select").get(0);
    var otroSelect  = otroForm.find(".servicio select").get(0);

    return unSelect.selectedIndex == otroSelect.selectedIndex;
}

function compararProductos(unForm, otroForm){

    var unSelect    = unForm.find(".producto select").get(0);
    var otroSelect  = otroForm.find(".producto select").get(0);

    return unSelect.selectedIndex == otroSelect.selectedIndex;
}

function reemplazarServicios(destino, origen){

    var d,o;

    d = destino.find(".form-group.cantidad input").first();
    o = origen.find(".form-group.cantidad input").first();
    d.val( o.val() );
    
    if ( destino.find(".form-group.observaciones textarea").length ){ 
        d = destino.find(".form-group.observaciones textarea").first();
        o = origen.find(".form-group.observaciones textarea").first();
        d.val( o.val() );
    }
        
    d = destino.find(".form-group.ORDER input").first();
    o = origen.find(".form-group.ORDER input").first();
    d.attr("value", o.attr("value"));

    d = destino.find(".form-group.DELETE input").first();
    d.attr("value", "");
    
    o = origen.find(".form-group.DELETE input").first();
    o.attr("value", "true");
}

function reemplazarProductos(destino, origen){

    var d,o;

    d = destino.find(".form-group.cantidad input").first();
    o = origen.find(".form-group.cantidad input").first();
    d.val( o.val() );
    
    d = destino.find(".form-group.ORDER input").first();
    o = origen.find(".form-group.ORDER input").first();
    d.attr("value", o.attr("value"));

    d = destino.find(".form-group.DELETE input").first();
    d.attr("value", "");

    o = origen.find(".form-group.DELETE input").first();
    o.attr("value", "true");
}

function unificar(argumentos){

    var i, j;
    var pos, mantener, eliminar;
    var a_reemplazar = [];
    
    var reemplazar = argumentos["reemplazador"];
    var comparar   = argumentos["comparador"];
    var formset      = document.getElementById(argumentos["formset_id"]);
    var habilitados = formset.getElementsByClassName("formset-form habilitado");
    var deshabilitados = formset.getElementsByClassName("formset-form deshabilitado");
    
    for (i=0 ; i<deshabilitados.length ; i++){
        for (j=0 ; j<habilitados.length ; j++){
            if ( comparar($(deshabilitados[i]), $(habilitados[j])) ){
                a_reemplazar.push({ "deshabilitado":deshabilitados[i], "habilitado":habilitados[j] });
            }
        }
    }

    for (n=0 ; n<a_reemplazar.length ; n++){
        
        mantener = $(a_reemplazar[n]["deshabilitado"]);
        eliminar = $(a_reemplazar[n]["habilitado"]);
        pos = eliminar.index()
        reemplazar(mantener, eliminar);
    }
}

function validarFormset(event, argumentos){

    var i, j, nuevoDuplicado;
    var duplicados  = false;
    var reemplazar = argumentos["reemplazador"];
    var comparar   = argumentos["comparador"];
    var prefix         = argumentos["formset_id"].slice(4);
    var formset      = document.getElementById(argumentos["formset_id"]);
    var habilitados = formset.getElementsByClassName("formset-form habilitado");

    for (i=0 ; i<habilitados.length ; i++)
        $(habilitados[i]).removeClass("has-error");
    
    for (i=0 ; i<habilitados.length ; i++){
        este = $(habilitados[i]);

        for (j=0 ; j<habilitados.length ; j++){
            if (i == j)
                continue;

            aquel = $(habilitados[j]);

            nuevoDuplicado = comparar(este, aquel);
            duplicados |= nuevoDuplicado;
            if (nuevoDuplicado)
                aquel.addClass("has-error");
        }

        if (duplicados){
            este.addClass("has-error");
            break;
        }
    }

    if (duplicados){
        $("#"+argumentos["error"]).removeClass("hidden");
        return false;
    }

    unificar(argumentos);
    return true;
}

function validarAccion(event){

    var accion = event.explicitOriginalTarget.value;
    var select = $(event.target).find(".form-group.mascota").first(); 
    var mascota = select.find("select").get(0).selectedIndex;
    var valida = ("presupuestada" == accion) || (mascota != 0);

    if (!valida)
        select.addClass("has-error");

    return valida;
}

function validar(event){

    var validador, argumentos;
    var submit = true;
    var n, num_validadores = validadores.length;

    for (n=0 ; n<num_validadores ; n++){

        validador = validadores[n]["validador"];
        argumentos = validadores[n]["argumentos"];

        if ( !validador(event, argumentos) )
            submit = false;
    }

    if (!submit){
        event.preventDefault();
    }
}

var agenda = $("<div>");

function verAgenda(){
    var value = $(this).val();
    var [dia, mes, anio] = value.split(" ")[0].split("/");
    var template = function(data) {
        var servicios = data.servicios.map(function(servicio) { return `${servicio}`}).join(", ");
        return `
        <table style="text-align: center;" class="table agendaListado">
        <thead>
        <tr>
        <th id="agenda-turno" style="text-align: center; width: 20%;"> Turno </th>
        <th id="agenda-duracion" style="text-align: center; width: 10%;"> Duracion </th>
        <th id="agenda-servicios" style="text-align: center; width: 70%;"> Servicios </th>
        </tr>
        </thead>
        <tbody>
        <tr>
        <br>
        <td><p>${(new Date(Date.parse(data.turno))).toLocaleTimeString()}</p></td>
        <td><p>${data.duracion}min</p></td>
        <td><p>${servicios}</p></td>
        </tr>
        </tbody>
        </table>`;//Se podria usar liibrerias que te permiten insertar codigo html underscore jq
    }
    $.ajax({
        url: "/cirugias/verAgenda",
        data: {fecha: `${anio}-${mes}-${dia}`},
        success: function(data) {
            var html = data.turnos.map(template).join(" ");
            agenda.html(`<table><th><p>Agenda del Dia </p></th>${html}</table>`);
            //var c = document.getElementById('id_agenda').value;
            //print(c);
            /*document.getElementById('id_inicio').onchange = function(){
                var c = document.getElementById('id_inicio').value;
                document.getElementById('id_agenda').innerHTML = c;
            }*/
        }
    })

}

$("#id_inicio").after(agenda);
$("#id_inicio").on("change", verAgenda);

$(function () {
        var today = new Date();
        var date = today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate();
        var time = today.getHours() + ":" + today.getMinutes();
        var dateTime = date+' '+time;
        $("#id_inicio").datetimepicker({
            locale: 'es',
        });

});