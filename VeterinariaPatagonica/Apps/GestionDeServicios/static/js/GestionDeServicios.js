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
		console.log("ADD - Total al iniciar = %d",total);
		if (total < max) {
			let field = template.replace(RegExp(`form-.`,"g"), `form-${total}`);
			total += 1;
			field = `<div class="col-xs-7" id="item-${total -1}">${field}</div>`;
			$("#id_form-TOTAL_FORMS").val(total);
			$buttons.before(field);
		} else{ console.log("Número máximo de productos alcanzado. NUMERO MAXIMO = %d",total)}
		console.log("ADD - Total al finalizar = %d",total);
	}

/*
	let remove = function(e) {
		let item = e.currentTarget.parentNode.id.split('-')[1];
		if (total > min) {
			total -= 1;
			$(`#item-${item}`).remove();
			$("#id_form-TOTAL_FORMS").val(total);
		}
	}
*/

	let removeSpecificItem = function(item){
		console.log("REMOVE SPECIFIC ITEM - Total al iniciar = %d",total);
		let numeroItem = item.currentTarget.parentNode.id.split('-')[1];
		if (total > min) {
			total -= 1;
			$(`#item-${numeroItem}`).remove();
			$("#id_form-TOTAL_FORMS").val(total);
			delete this.get;//¿¿¿ASI BORRO LA RELACION DEL ProductoServicio CON EL Servicio???
		}
		console.log("REMOVE SPECIFIC ITEM - Total al finalizar = %d",total);
	}


	let remove = function(){
		console.log("REMOVE - Total al iniciar = %d",total);
		if(total > min ){
			total-=1;
			$(`#item-${total}`).remove();
			$("#id_form-TOTAL_FORMS").val(total);
		}
		console.log("REMOVE- Total al finalizar = %d",total);
	}

	$("#button-remove").click(remove);
	$(document).on("click",".rm",removeSpecificItem);
	$("#button-add").click(add);

});
