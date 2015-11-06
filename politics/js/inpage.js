function scrollTo(id){
	if (id){
		scrollpos = $("#"+id).offset().top - 100;
		console.log($("#"+id).offset().top)
		$('html, body').animate({
	        scrollTop: scrollpos
	    }, 500);
	}
}

$( document ).ready(function() {
	var pos = getParameterByName('pos');
	console.log(pos);
	scrollTo(pos);
})