;(function() {

    let mostrar = function(){
      console.log("Imprimo desde la función");
    }


    let obtenerTotal = function(id){
      console.log("OBTENER TOTAL - entrando a la función.");
      let item = $(`#item-${id+1}`);
      let $item = $(item);
      let inputCantidad =$(`#id_form-${id}-cantidad`, $item[0]);
      let inputSelect = $(`#id_form-${id}-producto`,$item[0]);
      let $inputSelect = $(inputSelect)

      let cantidad = inputCantidad[0].value;

      let texto = $inputSelect.find(":selected").text();

      if ((texto != "---------") && (cantidad)) {
        let varParseo = $inputSelect.find(":selected").text();
        varParseo = varParseo.split(",");
        varParseo = varParseo[2];
        varParseo = varParseo.split(" ");
        varParseo = varParseo[2];
        precio = parseInt(varParseo);
        precioFinal = precio * cantidad
        console.log("El precio de la tupla completa es: %s",precioFinal);
        let inputTotal=$(`#id_total`);
        let total = parseInt(inputTotal[0].value);
        total += precioFinal;
        console.log(total);
        document.getElementById("id_total").value = total;

      }else{
        console.log("No se puede calcular el precio, falta llenar algún campo.");

      }
    console.log("OBTENER TOTAL - finalizando la función.");
    }

    let totalTuplas = Number($("#id_form-TOTAL_FORMS").val());
  	let initial = $("#id_form-INITIAL_FORMS").val();
  	let min = Number($("#id_form-MIN_NUM_FORMS").val());
  	let max = Number($("#id_form-MAX_NUM_FORMS").val());

  	let $buttons = $("#buttons");
  	let template = $(`#item-${totalTuplas}`).html().replace(RegExp(`form-${totalTuplas - 1}`,"g"), `form-ITEM`);
    //console.log(template);
  	let add = function() {
  		console.log("ADD - Total al iniciar = %d",totalTuplas);
  		if (totalTuplas < max) {
        let id = totalTuplas;
        let field = template.replace(RegExp(`form-ITEM`,"g"), `form-${id}`);
  			totalTuplas += 1;
  			field = `<div class="col-xs-7" id="item-${totalTuplas}">${field}</div>`;
  			$("#id_form-TOTAL_FORMS").val(totalTuplas);
        let $field = $(field);
        $buttons.before($field);
        let cantidad =$(`#id_form-${id}-cantidad`, $field).on("input", function() { obtenerTotal(id); });//Obtengo la cantidad del elemento recien agregado
        let producto = document.querySelector(`select[name="form-${id}-producto"]`, $field);
        producto.onchange=function(e) {
          obtenerTotal(id);
        };
        //let producto =$(`#id_form-${id}-producto`, $field).on("change", function() {obtenerTotal(id); });


  		} else{ console.log("Número máximo de productos alcanzado. NUMERO MAXIMO = %d",totalTuplas)}
  		console.log("ADD - Total al finalizar = %d",totalTuplas);
  	}
  	$("#button-add").click(add);

  //Forma de hacer el calculo de subtotal y total

    function calculo(cantidad,precio,inputtext,totaltext){
    // Calculo del subtotal
    subtotal = precio*cantidad;
    inputtext.value=subtotal;

          //Calculo del total
    total = eval(totaltext.value);
    totaltext.value = total + subtotal;
    }
})();


/*$(document).ready(function() {

    $('.facturas-form-linkinfo').each(function(i,x){
        $(x).click(function(e){

            var a = $(e.target).attr('for');
            $('#'+a).toggle();
        });
    });
})*/







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
