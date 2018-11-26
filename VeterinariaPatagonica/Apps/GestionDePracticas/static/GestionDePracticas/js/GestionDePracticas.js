function getForms(formset){
    var forms = formset.getElementsByClassName("forms")[0];
    var formsetforms = forms.getElementsByClassName("formset-form");
    return formsetforms;
}

function getPrimerEliminar(forms){
    var formgroup = forms[0].getElementsByClassName("form-group eliminar")[0];
    var a = formgroup.getElementsByTagName("a")[0];
    return a;
}

function antecesorSegunClase(item, clase){
    var i = item;
    while( ! i.classList.contains(clase) ){
        i = i.parentElement;
    }

    return i;
}

function actualizarEliminar(formset){

    var items = getForms(formset);

    if (items.length < 2)
        getPrimerEliminar(items).classList.add("disabled");
    else
        getPrimerEliminar(items).classList.remove("disabled");
}

function numeroDeForm(form){

    var n;
    var forms = antecesorSegunClase(form, "forms").children;
    for (n=0 ; n<forms.length ; n++){
        if ( forms[n] == form )
            return n;
    }
    return -1;
}

function eliminar(event){

    event.preventDefault();

    var formset = antecesorSegunClase(event.target, "formset");
    var forms = getForms(formset);
    if (forms.length < 2)
        return;

    var form = antecesorSegunClase(event.target, "formset-form");
    var pos = numeroDeForm(form);
    var prefix = formset.id.replace("-formset","");

    eliminarForm(form, prefix, pos);

    forms = getForms(formset);
    if (forms.length < 2)
        actualizarEliminar(formset);
}

function eliminarForm(form, prefix, pos){

    var sig = form.nextElementSibling;
    form.remove();
    
    while (sig != null) {
        cambiarId(sig, prefix, pos);
        pos++;
        sig = sig.nextElementSibling;
    }

    actualizarTotal(prefix, pos);
}

function actualizarTotal(prefix, cantidad){

    document.getElementById('id_'+prefix+'-TOTAL_FORMS').value = cantidad;
}

function agregarForm(formset, form){

    var forms = formset.getElementsByClassName("forms")[0];
    forms.appendChild(form);
}

function agregar(event){

    var formset = antecesorSegunClase(event.target, "formset");
    var forms = getForms(formset);
    var prefix = formset.id.replace("-formset","");
    var nuevaCantidad = forms.length+1

    var nuevo_id = forms.length;
    var emptyform = formset.getElementsByClassName("emptyform")[0].children[0];
    var nuevo = emptyform.cloneNode(true);

    cambiarId(nuevo, prefix, nuevo_id);
    agregarForm(formset, nuevo);

    actualizarTotal(prefix, nuevaCantidad);
    if (nuevaCantidad == 2){
        actualizarEliminar(formset);
    }
}

function cambiarId(form, prefix, id){

    var i, j, tags;
    var tagNames = ["input", "textarea", "select", "label"];

    for (j=0 ; j<tagNames.length ; j++){
        
        tags = form.getElementsByTagName(tagNames[j]);

        for (i=0 ; i<tags.length ; i++){
            actualizarAttr(tags[i], "id", "id_"+prefix, id);
            actualizarAttr(tags[i], "name", prefix, id);
            actualizarAttr(tags[i], "for", prefix, id);
        }
    }
}

function actualizarAttr(item, attrName, start, id){

    var nuevo, campo
    var attr = item.attributes.getNamedItem(attrName);

    if ( attr != null && attr.value.startsWith(start+"-") ){
            campo = attr.value.split("-")[2];
            nuevo = [start, id, campo].join("-");
            attr.value = nuevo;
    }
}

function buscarOpcion(form, clase){

    var contenedor = form.getElementsByClassName(clase)[0];
    var select    = contenedor.getElementsByTagName("select")[0];
    return select.selectedIndex;
}

function compararServicios(form1, form2){

    var opcion1 = buscarOpcion(form1, "form-group servicio");
    var opcion2 = buscarOpcion(form2, "form-group servicio");
    
    return opcion1 == opcion2;
}


function compararProductos(form1, form2){

    var opcion1 = buscarOpcion(form1, "form-group producto");
    var opcion2 = buscarOpcion(form2, "form-group producto");
    
    return opcion1 == opcion2;
}

function agregarError(donde, mensaje){

    var lista, item, texto, errores;
    var esta = donde.getElementsByClassName("errores");

    if (esta.length > 0){
        errores = esta[0];
        lista = errores.getElementsByTagName("ul")[0];
    }
    else{
        var div = document.createElement("div");
        div.innerHTML = '<strong>Por favor revise los siguientes errores:</strong><ul></ul>';
        div.classList.add("errores");
        donde.appendChild(div);
        lista = div.getElementsByTagName("ul")[0];
    }

    item = document.createElement("li");
    texto = document.createElement("p");
    texto.innerHTML = mensaje;
    item.appendChild(texto);
    item.classList.add("dinamico");
    lista.appendChild(item);
}

function resetValidacion(forms, errores){
    
    var i, itemsErrores, cuadroErrores;
    
    for (i=0 ; i<forms.length ; i++)
        forms[i].classList.remove("has-error");
    
    itemsErrores = errores.getElementsByClassName("dinamico");
    for (i=0 ; i<itemsErrores.length ; i++)
        itemsErrores[i].remove();

    cuadroErrores = errores.getElementsByClassName("errores");
    if (cuadroErrores.length > 0){
        cuadroErrores = cuadroErrores[0];
        itemsErrores = cuadroErrores.getElementsByTagName("li");
        if (itemsErrores.length <= 0)
            cuadroErrores.remove();
    }
}

function validarFormset(event, argumentos){

    var i, j, nuevoDuplicado, mensaje, items;
    var duplicados  = Array();
    var comparar   = argumentos["comparador"];
    var formset      = document.getElementById(argumentos["formset_id"]);
    var forms         = getForms(formset);
    var errores      = argumentos["errores"];
    var objeto      = argumentos["objeto"];

    resetValidacion(forms, errores);
    
    for (i=0 ; i<forms.length ; i++){
        for (j=0 ; j<forms.length ; j++){
            if (i == j)
                continue;

            nuevoDuplicado = comparar(forms[i], forms[j]);
            if (nuevoDuplicado){
                forms[j].classList.add("has-error");
                duplicados.push(j+1);
            }
        }

        if (duplicados.length > 0){
            forms[i].classList.add("has-error");
            duplicados.push(i+1);
            break;
        }
    }

    if (duplicados.length){
        duplicados.sort();
        items = duplicados.join(", ");
        mensaje = "Cada item puede agregarse a lo sumo una vez, revise las filas: "+items;
        agregarError(errores, mensaje);
        return false;
    }

    return true;
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
            //document.getElementById('id_inicio').onchange = function(){
                //var c = document.getElementById('id_inicio').value;
                //document.getElementById('id_agenda').innerHTML = c;
            //}
        }
    })

}

$("#id_inicio").after(agenda);
$("#id_inicio").on("change", verAgenda);
