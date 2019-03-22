/**
 * Resize function without multiple trigger
 * 
 * Usage:
 * $(window).smartresize(function(){  
 *     // code here
 * });
 */
(function($,sr){
    // debouncing function from John Hann
    // http://unscriptable.com/index.php/2009/03/20/debouncing-javascript-methods/
    var debounce = function (func, threshold, execAsap) {
      var timeout;

        return function debounced () {
            var obj = this, args = arguments;
            function delayed () {
                if (!execAsap)
                    func.apply(obj, args); 
                timeout = null; 
            }

            if (timeout)
                clearTimeout(timeout);
            else if (execAsap)
                func.apply(obj, args);

            timeout = setTimeout(delayed, threshold || 100); 
        };
    };

    // smartresize 
    jQuery.fn[sr] = function(fn){  return fn ? this.bind('resize', debounce(fn)) : this.trigger(sr); };

})(jQuery,'smartresize');
/**
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

$(document).ready(function() {
            
    init_sidebar();				
});	

var CURRENT_URL = window.location.href.split('#')[0].split('?')[0],
    $BODY = $('body'),
    $MENU_TOGGLE = $('#menu_toggle'),
    $SIDEBAR_MENU = $('#sidebar-menu'),
    $SIDEBAR_FOOTER = $('.sidebar-footer'),
    $LEFT_COL = $('.left_col'),
    $RIGHT_COL = $('.right_col'),
    $NAV_MENU = $('.nav_menu'),
    $FOOTER = $('footer');

	
	
// Sidebar
function init_sidebar() {
// TODO: This is some kind of easy fix, maybe we can improve this
var setContentHeight = function () {
	// reset height
	$RIGHT_COL.css('min-height', $(window).height());

	var bodyHeight = $BODY.outerHeight(),
		footerHeight = $BODY.hasClass('footer_fixed') ? -10 : $FOOTER.height(),
		leftColHeight = $LEFT_COL.eq(1).height() + $SIDEBAR_FOOTER.height(),
		contentHeight = bodyHeight < leftColHeight ? leftColHeight : bodyHeight;

	// normalize content
	contentHeight -= $NAV_MENU.height() + footerHeight;

	$RIGHT_COL.css('min-height', contentHeight);
};

  $SIDEBAR_MENU.find('a').on('click', function(ev) {
	  console.log('clicked - sidebar_menu');
        var $li = $(this).parent();

        if ($li.is('.active')) {
            $li.removeClass('active active-sm');
            $('ul:first', $li).slideUp(function() {
                setContentHeight();
            });
        } else {
            // prevent closing menu if we are on child menu
            if (!$li.parent().is('.child_menu')) {
                $SIDEBAR_MENU.find('li').removeClass('active active-sm');
                $SIDEBAR_MENU.find('li ul').slideUp();
            }else
            {
				if ( $BODY.is( ".nav-sm" ) )
				{
					$li.parent().find( "li" ).removeClass( "active active-sm" );
					$li.parent().find( "li ul" ).slideUp();
				}
			}
            $li.addClass('active');

            $('ul:first', $li).slideDown(function() {
                setContentHeight();
            });
        }
    });

// toggle small or large menu 
$MENU_TOGGLE.on('click', function() {
		console.log('clicked - menu toggle');
		
		if ($BODY.hasClass('nav-md')) {
			$SIDEBAR_MENU.find('li.active ul').hide();
			$SIDEBAR_MENU.find('li.active').addClass('active-sm').removeClass('active');
		} else {
			$SIDEBAR_MENU.find('li.active-sm ul').show();
			$SIDEBAR_MENU.find('li.active-sm').addClass('active').removeClass('active-sm');
		}

	$BODY.toggleClass('nav-md nav-sm');

	setContentHeight();

	$('.dataTable').each ( function () { $(this).dataTable().fnDraw(); });
});

	// check active menu
	$SIDEBAR_MENU.find('a[href="' + CURRENT_URL + '"]').parent('li').addClass('current-page');

	$SIDEBAR_MENU.find('a').filter(function () {
		return this.href == CURRENT_URL;
	}).parent('li').addClass('current-page').parents('ul').slideDown(function() {
		setContentHeight();
	}).parent().addClass('active');

	// recompute content when resizing
	$(window).smartresize(function(){  
		setContentHeight();
	});

	setContentHeight();

	// fixed sidebar
	if ($.fn.mCustomScrollbar) {
		$('.menu_fixed').mCustomScrollbar({
			autoHideScrollbar: true,
			theme: 'minimal',
			mouseWheel:{ preventDefault: true }
		});
	}
};
// /Sidebar



/*
        Formsets: productos y servicios
*/

function getForms(formset){
    var forms = formset.getElementsByClassName("forms")[0];
    var formsetforms = forms.getElementsByClassName("formset-form");
    return formsetforms;
}

function getPrimerEliminar(forms){
    var formgroup = forms[0].getElementsByClassName("form-group eliminar")[0];
    var a = formgroup.getElementsByTagName("a")[0];
    return a;
}

function antecesorSegunClase(item, clase){
    var i = item;
    while( ! i.classList.contains(clase) ){
        i = i.parentElement;
    }

    return i;
}

function actualizarEliminar(formset){

    var items = getForms(formset);

    if (items.length < 2)
        getPrimerEliminar(items).classList.add("disabled");
    else
        getPrimerEliminar(items).classList.remove("disabled");
}

function numeroDeForm(form){

    var n;
    var forms = antecesorSegunClase(form, "forms").children;
    for (n=0 ; n<forms.length ; n++){
        if ( forms[n] == form )
            return n;
    }
    return -1;
}

function eliminar(event){

    event.preventDefault();

    var formset = antecesorSegunClase(event.target, "formset");
    var forms = getForms(formset);
    if (forms.length < 2)
        return;

    var form = antecesorSegunClase(event.target, "formset-form");
    var pos = numeroDeForm(form);
    var prefix = formset.id.replace("-formset","");

    eliminarForm(form, prefix, pos);

    forms = getForms(formset);
    if (forms.length < 2)
        actualizarEliminar(formset);
}

function eliminarForm(form, prefix, pos){

    var sig = form.nextElementSibling;
    form.remove();
    
    while (sig != null) {
        cambiarId(sig, prefix, pos);
        pos++;
        sig = sig.nextElementSibling;
    }

    actualizarTotal(prefix, pos);
}

function actualizarTotal(prefix, cantidad){

    document.getElementById('id_'+prefix+'-TOTAL_FORMS').value = cantidad;
}

function agregarForm(formset, form){

    var forms = formset.getElementsByClassName("forms")[0];
    forms.appendChild(form);
}

function agregar(event){

    var formset = antecesorSegunClase(event.target, "formset");
    var forms = getForms(formset);
    var prefix = formset.id.replace("-formset","");
    var nuevaCantidad = forms.length+1

    var nuevo_id = forms.length;
    var emptyform = formset.getElementsByClassName("emptyform")[0].children[0];
    var nuevo = emptyform.cloneNode(true);

    cambiarId(nuevo, prefix, nuevo_id);
    agregarForm(formset, nuevo);

    actualizarTotal(prefix, nuevaCantidad);
    if (nuevaCantidad == 2){
        actualizarEliminar(formset);
    }
}

function cambiarId(form, prefix, id){

    var i, j, tags;
    var tagNames = ["input", "textarea", "select", "label"];

    for (j=0 ; j<tagNames.length ; j++){
        
        tags = form.getElementsByTagName(tagNames[j]);

        for (i=0 ; i<tags.length ; i++){
            actualizarAttr(tags[i], "id", "id_"+prefix, id);
            actualizarAttr(tags[i], "name", prefix, id);
            actualizarAttr(tags[i], "for", prefix, id);
        }
    }
}

function actualizarAttr(item, attrName, start, id){

    var nuevo, campo
    var attr = item.attributes.getNamedItem(attrName);

    if ( attr != null && attr.value.startsWith(start+"-") ){
            campo = attr.value.split("-")[2];
            nuevo = [start, id, campo].join("-");
            attr.value = nuevo;
    }
}

function buscarOpcion(form, clase){

    var contenedor = form.getElementsByClassName(clase)[0];
    var select    = contenedor.getElementsByTagName("select")[0];
    return select.selectedIndex;
}

function compararServicios(form1, form2){

    var opcion1 = buscarOpcion(form1, "form-group servicio");
    var opcion2 = buscarOpcion(form2, "form-group servicio");
    
    return opcion1 == opcion2;
}


function compararProductos(form1, form2){

    var opcion1 = buscarOpcion(form1, "form-group producto");
    var opcion2 = buscarOpcion(form2, "form-group producto");
    
    return opcion1 == opcion2;
}

function agregarError(donde, mensaje){

    var lista, item, texto, errores;
    var esta = donde.getElementsByClassName("errores");

    if (esta.length > 0){
        errores = esta[0];
        lista = errores.getElementsByTagName("ul")[0];
    }
    else{
        var div = document.createElement("div");
        div.innerHTML = '<strong>Por favor revise los siguientes errores:</strong><ul></ul>';
        div.classList.add("errores");
        donde.appendChild(div);
        lista = div.getElementsByTagName("ul")[0];
    }

    item = document.createElement("li");
    texto = document.createElement("p");
    texto.innerHTML = mensaje;
    item.appendChild(texto);
    item.classList.add("dinamico");
    lista.appendChild(item);
}

function resetValidacion(forms, errores){
    
    var i, itemsErrores, cuadroErrores;
    
    for (i=0 ; i<forms.length ; i++)
        forms[i].classList.remove("has-error");
    
    itemsErrores = errores.getElementsByClassName("dinamico");
    for (i=0 ; i<itemsErrores.length ; i++)
        itemsErrores[i].remove();

    cuadroErrores = errores.getElementsByClassName("errores");
    if (cuadroErrores.length > 0){
        cuadroErrores = cuadroErrores[0];
        itemsErrores = cuadroErrores.getElementsByTagName("li");
        if (itemsErrores.length <= 0)
            cuadroErrores.remove();
    }
}

function validarFormset(event, argumentos){

    var i, j, nuevoDuplicado, mensaje, items;
    var duplicados  = Array();
    var comparar   = argumentos["comparador"];
    var formset      = document.getElementById(argumentos["formset_id"]);
    var forms         = getForms(formset);
    var errores      = argumentos["errores"];

    resetValidacion(forms, errores);
    
    for (i=0 ; i<forms.length ; i++){
        for (j=0 ; j<forms.length ; j++){
            if (i == j)
                continue;

            nuevoDuplicado = comparar(forms[i], forms[j]);
            if (nuevoDuplicado){
                forms[j].classList.add("has-error");
                duplicados.push(j+1);
            }
        }

        if (duplicados.length > 0){
            forms[i].classList.add("has-error");
            duplicados.push(i+1);
            break;
        }
    }

    if (duplicados.length){
        duplicados.sort();
        items = duplicados.join(", ");
        mensaje = "Cada item puede agregarse a lo sumo una vez, revise las filas: "+items;
        agregarError(errores, mensaje);
        return false;
    }

    return true;
}

function validar(event){

    var validador, argumentos;
    var submit = true;
    var n, num_validadores = validadores.length;

    for (n=0 ; n<num_validadores ; n++){

        validador = validadores[n]["validador"];
        argumentos = validadores[n]["argumentos"];

        if ( !validador(event, argumentos) )
            submit = false;
    }

    if (!submit){
        event.preventDefault();
    }
}

function ajustarDuracion(id_desde, id_hasta, id_duracion){
    var input = document.getElementById(id_duracion);
    var duracion = parseInt(input.value);
 
    var desde = document.getElementById(id_desde);
    var desde_fmt = $(desde).data("DateTimePicker").date()._f;
    var d = desde.getElementsByTagName("input")[0];
 
    var hasta = document.getElementById(id_hasta);
    var hasta_fmt = $(hasta).data("DateTimePicker").date()._f;
    var h = hasta.getElementsByTagName("input")[0];
 
    var x = moment(d.value, desde_fmt);
    x.add(duracion, "minute");
    h.value = x.format(hasta_fmt);
    return;
}

function calcularDuracion(id_desde, id_hasta){
    var desde = document.getElementById(id_desde);
    var hasta = document.getElementById(id_hasta);
    var desde_fmt = $(desde).data("DateTimePicker").date()._f;
    var hasta_fmt = $(hasta).data("DateTimePicker").date()._f;
    var desde_val = desde.getElementsByTagName("input")[0].value;
    var hasta_val = hasta.getElementsByTagName("input")[0].value;
    var a = moment(desde_val, desde_fmt);
    var b = moment(hasta_val, hasta_fmt);
    return b.diff(a,"minute",false);
}






function leerFormato(id_datetimepicker){
    var datetimepicker = document.getElementById(id_datetimepicker);
    return $(datetimepicker).data("DateTimePicker").date()._f;
}

function calcularVigencia(id_desde, id_hasta, formato, unidad){

    var desde_value = document.getElementById(id_desde).value;
    var hasta_value = document.getElementById(id_hasta).value;

    var desde_moment = moment(desde_value, formato);
    var hasta_moment = moment(hasta_value, formato);

    return hasta_moment.diff(desde_moment,unidad,false);
}

function ajustarVigencia(id_desde, id_hasta, id_duracion, formato, unidad){

    var duracion = parseInt(document.getElementById(id_duracion).value);
 
    var desde = document.getElementById(id_desde); 
    var hasta = document.getElementById(id_hasta);
    var nuevo_hasta = moment(desde.value, formato);

    nuevo_hasta.add(duracion, unidad);
    hasta.value = nuevo_hasta.format(formato);
    return;
}