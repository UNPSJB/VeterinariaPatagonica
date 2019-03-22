/*var agenda = $("<div>");

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
*/