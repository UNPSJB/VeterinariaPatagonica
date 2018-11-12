$(function() {

  let total = Number($("#id_form-TOTAL_FORMS").val());
  let initial = $("#id_form-INITIAL_FORMS").val();
  let min = Number($("#id_form-MIN_NUM_FORMS").val());
  let max = Number($("#id_form-MAX_NUM_FORMS").val());

  let $buttons = $("#buttons");
  let template = $(`#item-${total}`).html().replace(RegExp(`form-${total - 1}`,"g"), `form-ITEM`);

  console.log("Template: %s", template);

  let add = function() {
		console.log("ADD - Total al iniciar = %d",total);
		if (total < max) {
			let field = template.replace(RegExp(`form-ITEM`,"g"), `form-${total}`);
			total += 1;
			field = `<div class="col-xs-7" id="item-${total}">${field}</div>`;
			$("#id_form-TOTAL_FORMS").val(total);
			$buttons.before(field);
		} else{ console.log("Número máximo de productos alcanzado. NUMERO MAXIMO = %d",total)}
		console.log("ADD - Total al finalizar = %d",total);
	}
	$("#button-add").click(add);

});


/*$(document).ready(function() {

    $('.facturas-form-linkinfo').each(function(i,x){
        $(x).click(function(e){

            var a = $(e.target).attr('for');
            $('#'+a).toggle();
        });
    });
})*/




//Forma de hacer el calculo de subtotal y total
/*
  function calculo(cantidad,precio,inputtext,totaltext){

	// Calculo del subtotal
	subtotal = precio*cantidad;
	inputtext.value=subtotal;

        //Calculo del total
	total = eval(totaltext.value);
	totaltext.value = total + subtotal;
  }
*/



/*function sumaItems()
{
    function getVal(item)
    {
        if(document.getElementById(item).value != “”)
            return parseFloat(document.getElementById(item).value);
        else
            return 0;
}
document.getElementById(‘PX_TOTAL’).value =
getVal(‘PX_1’) + getVal(‘PX_2’);
}*/




/*
	let add = function() {
		if (total < max) {
			let field = template.replace(RegExp(`form-ITEM`,"g"), `form-${total}`);
			field = `<div class="col-sm-8" id="item-${total}">${field}</div>`;
			total += 1;
			$("#id_form-TOTAL_FORMS").val(total);
			$buttons.before(field);
		}
	}
*/
//	$("#button-add").click(add);
