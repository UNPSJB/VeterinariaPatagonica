$(function() {
	let total = Number($("#id_form-TOTAL_FORMS").val());
	let initial = $("#id_form-INITIAL_FORMS").val();
	let min = $("#id_form-MIN_NUM_FORMS").val();
	let max = $("#id_form-MAX_NUM_FORMS").val();

	let add = function() {
		let field = $("#formset-template").html().replace(/form-\d+/g, `form-${total}`);
		total += 1;
		$("#button-add").before(field);
		$("#id_form-TOTAL_FORMS").val(total);
		console.log(total);
	}
	window.add = add;
});
