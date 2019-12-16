$(document).ready(function() {

    $('.rubros-form-linkinfo').each(

            function(i,x){

                $(x).click(function(e){

                     var a = $(e.target).attr('for');
                     $('#'+a).toggle();
        });
    });

});