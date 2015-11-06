function scrollTo(id){
	if (id){
		scrollpos = $("#"+id).offset().top - 100;
		console.log($("#"+id).offset().top)
		$('html, body').animate({
	        scrollTop: scrollpos
	    }, 500);
	}
}