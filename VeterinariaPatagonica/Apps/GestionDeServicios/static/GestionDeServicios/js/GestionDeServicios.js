$(function() {
	let total = Number($("#id_form-TOTAL_FORMS").val());
	let initial = $("#id_form-INITIAL_FORMS").val();
	let min = $("#id_form-MIN_NUM_FORMS").val();
	let max = $("#id_form-MAX_NUM_FORMS").val();

	let add = function() {
		let field = $("#formset-template").html().replace(RegExp(`form-${initial}`,"g"), `form-${total}`);
		total += 1;
		$("#formset-template").after(field);
	}
	let quitar = function(){
		let field = $("#formset-template").html();//Hacer aca en esta linea que señale lo que queiro borrar algo asi como remove(/form-\d+/g, `form-${total}`) pero no funciona asi. ni con removeChild()
		if (total > 1){
			total -= 1;
			//$("#button-quitar").before(field); tendria que borrarlo aca parece.
			$("#id_form-TOTAL_FORMS").val(total);
			console.log(total);
		} else{
			alert("Imposible eliminar el Producto, el Servicio debe tener almenos un Producto.");
		}
	}
	window.quitar = quitar;
	window.add = add;
});
