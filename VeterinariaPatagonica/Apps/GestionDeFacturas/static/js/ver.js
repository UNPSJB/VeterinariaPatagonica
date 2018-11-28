$(function() {

  let $botonPagar = $("#facturaHabilitadosCrear");
  let $esPagada = $("#esPagada");
  let textoPagada = $esPagada.text();
  let arrayEsPagada = textoPagada.split(":");
  console.log(arrayEsPagada[1]);
  if (arrayEsPagada[1] == " Pagada"){
    $botonPagar.hide();
  }
});
