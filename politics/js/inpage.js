offset = $('#titlebar').height() + 50;

function scrollTo(id){
	scrollpos = $("#"+id).offset().top - 100;
	console.log($("#"+id).offset().top)
	$('html, body').animate({
        scrollTop: scrollpos
    }, 500);
	//$(window).scrollTop(scrollpos);
}

$( document ).ready(function() {
	var pos = getParameterByName('pos');
	console.log(offset);
	console.log(pos);
	scrollTo(pos);
})