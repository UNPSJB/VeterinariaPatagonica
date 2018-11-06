
/*$(document).ready(function() {

    $('.facturas-form-linkinfo').each(function(i,x){
        $(x).click(function(e){

            var a = $(e.target).attr('for');
            $('#'+a).toggle();
        });
    });
})*/

//Forma de hacer el calculo de subtotal y total
$ function calculo(cantidad,precio,inputtext,totaltext){

	// Calculo del subtotal
	subtotal = precio*cantidad;
	inputtext.value=subtotal;

        //Calculo del total
	total = eval(totaltext.value);
	totaltext.value = total + subtotal;
}


$(function() {
	let total = Number($("#id_form-TOTAL_FORMS").val());
	let initial = $("#id_form-INITIAL_FORMS").val();
	let min = Number($("#id_form-MIN_NUM_FORMS").val());
	let max = Number($("#id_form-MAX_NUM_FORMS").val());

	let $buttons = $("#buttons");
	let template = $("#formset-template").html().replace(RegExp(`form-${initial}`,"g"), `form-ITEM`);
	$("#formset-template").remove();
	total = total - 1;
	$("#id_form-TOTAL_FORMS").val(total);

	let add = function() {
		if (total < max) {
			let field = template.replace(RegExp(`form-ITEM`,"g"), `form-${total}`);
			field = `<div class="col-sm-8" id="item-${total}">${field}</div>`;
			total += 1;
			$("#id_form-TOTAL_FORMS").val(total);
			$buttons.before(field);
		}
	}

	let remove = function(e) {
		let item = e.currentTarget.parentNode.id.split('-')[1];
		if (total > min) {
			total -= 1;
			$(`#item-${item}`).remove();
			$("#id_form-TOTAL_FORMS").val(total);
		}
	}

	$(document).on("click",".rm",remove);
	$("#button-add").click(add);

});

