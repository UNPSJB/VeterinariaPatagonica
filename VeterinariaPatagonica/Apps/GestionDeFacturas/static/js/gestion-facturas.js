;(function() {


    let totalTuplas = Number($("#id_form-TOTAL_FORMS").val());
    let initial = $("#id_form-INITIAL_FORMS").val();
    let min = Number($("#id_form-MIN_NUM_FORMS").val());
    let max = Number($("#id_form-MAX_NUM_FORMS").val());

    let $buttons = $("#buttons");
    let template = $(`#item-${totalTuplas}`).html().replace(RegExp(`form-${totalTuplas - 1}`,"g"), `form-ITEM`);
    //console.log(template);
    let iterador = 0;
    for (iterador ; iterador<totalTuplas; iterador++){
      let cantidad =$(`#id_form-${iterador}-cantidad`).on("input", function() { calcularTotal(); });//Obtengo la cantidad del elemento recien agregado
      let producto = document.querySelector(`select[name="form-${iterador}-producto"]`);
      producto.onchange=function(e) {
        calcularTotal();
      };
      let borrar = $(`#id_form-${iterador}-DELETE`).on("change", function() { calcularTotal(); });
    }

    let calcularTotal = function(){
      let i=0;
      console.log("OBTENER TOTAL - entrando a la función.");
      let acumulador =0;
      for (i ; i<totalTuplas; i++){
        let item = $(`#item-${i+1}`);
        let $item = $(item);
        let inputCantidad =$(`#id_form-${i}-cantidad`, $item[0]);
        let inputSelect = $(`#id_form-${i}-producto`,$item[0]);
        let inputDelete = $(`#id_form-${i}-DELETE`, $item[0]);
        let $inputSelect = $(inputSelect);
        let borrar = inputDelete[0];
        let cantidad = inputCantidad[0].value;
        let texto = $inputSelect.find(":selected").text();
        //console.log(borrar.checked);
        if (borrar.checked == false){
          if (cantidad < 0){ cantidad = 0;}
          if ((texto != "---------") && (cantidad)) {
            let varParseo = $inputSelect.find(":selected").text();
            varParseo = varParseo.split(",");
            varParseo = varParseo[2];
            varParseo = varParseo.split(" ");
            varParseo = varParseo[2];
            let precioProducto = parseInt(varParseo);
            let precioFinalTupla = precioProducto * cantidad
            console.log("El precio de la tupla completa es: %s",precioFinalTupla);
            let inputTotal=$(`#id_total`);
            let precioTotal = parseInt(inputTotal[0].value);
            acumulador +=precioFinalTupla;
            console.log(precioTotal);
          }else{
            console.log("No se puede calcular el precio, falta llenar algún campo.");
          }
        }
      }
      document.getElementById("id_total").value = acumulador;
      console.log("OBTENER TOTAL - finalizando la función.");
    }

//Función que agrega un nuevo item (nueva tupla de selector de producto y cantidad). Asociandoles el comportamiento
//dinámico para calcular el total.
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
        let cantidad =$(`#id_form-${id}-cantidad`, $field).on("input", function() { calcularTotal(); });//Obtengo la cantidad del elemento recien agregado
        let producto = document.querySelector(`select[name="form-${id}-producto"]`, $field);
        producto.onchange=function(e) {
          calcularTotal();
        };
        let borrar = $(`#id_form-${id}-DELETE`, $field).on("change", function() { calcularTotal(); });
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
