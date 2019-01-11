$(document).ready(function() {

    $('.clientes-form-linkinfo').each(

            function(i,x){

                $(x).click(function(e){

                     var a = $(e.target).attr('for');
                     $('#'+a).toggle();
        });
    });


    function deshabilitarControlesC(e){
        var tipoDeCliente = document.querySelector('#id_tipoDeCliente').value;
        if (tipoDeCliente === "C") {

          $('input[data-tipo=especial]').parent().parent().hide()
        } else {

          $('input[data-tipo=especial]').parent().parent().show()
        }
    }


    var tipoCliente = document.querySelector('#id_tipoDeCliente').value

    if (tipoCliente === "C"){
            document.querySelector('#id_tipoDeCliente').onchange=deshabilitarControlesC;
            $('input[data-tipo=especial]').parent().parent().hide()
    }
    else if (tipoCliente === "E"){
        document.querySelector('#id_tipoDeCliente').onchange=deshabilitarControlesC;
         $('input[data-tipo=especial]').parent().parent().show()
    }

});