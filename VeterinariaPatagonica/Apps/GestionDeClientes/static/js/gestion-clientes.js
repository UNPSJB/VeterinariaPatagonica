$(document).ready(function() {

    $('.clientes-form-linkinfo').each(

            function(i,x){

                $(x).click(function(e){

                     var a = $(e.target).attr('for');
                     $('#'+a).toggle();
        });
    });


    function deshabilitarControles(e){
        var tipoDeCliente = document.querySelector('#id_tipoDeCliente').value;
        if (tipoDeCliente === "C") {

          $('input[data-tipo=especial]').parent().parent().hide()
        } else {

          $('input[data-tipo=especial]').parent().parent().show()
        }
    }

    document.querySelector('#id_tipoDeCliente').onchange=deshabilitarControles;
    $('input[data-tipo=especial]').parent().parent().hide()


});