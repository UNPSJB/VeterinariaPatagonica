$(function() {
	let total = Number($("#id_form-TOTAL_FORMS").val());
	let initial = $("#id_form-INITIAL_FORMS").val();
	let min = Number($("#id_form-MIN_NUM_FORMS").val());
	let max = Number($("#id_form-MAX_NUM_FORMS").val());

	let $buttons = $("#buttons");
	let template = $(`#item-${total}`).html().replace(RegExp(`form-${total - 1}`,"g"), `form-ITEM`);

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
