$(document).ready( function(){

    $('.mascotas-form-linkinfo').each(

        function(i,x){

            $(x).click(function(e){

                var a = $(e.target).attr('for');
                $('#'+a).toggle();
				}
            );
        }
    );


    /*$(function () {
            var today = new Date();
            var date = today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate();
            var time = today.getHours() + ":" + today.getMinutes();
            var dateTime = date+' '+time;
            $("#id_fechaNacimiento").datetimepicker({
                locale: 'es',
                format: 'L',
                maxDate: new Date()
            });

    });*/
});



