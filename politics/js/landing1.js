function scrollTo(id){
	if (id){
		scrollpos = $("#"+id).offset().top - 100;
		console.log($("#"+id).offset().top)
		$('html, body').animate({
	        scrollTop: scrollpos
	    }, 500);
	}
}

function abText(id){
	text = $("#"+id).html()
	$('#abilitytext').html(text)
}

function rhover(id){
	s1 = 'This is the text for stat 1'
	s2 = 'This is the text for stat 2'
	s3 = 'This is the text for stat 3'
	s4 = 'This is the text for stat 4'
	s5 = 'This is the text for stat 5'

	switch (id){
		case 'stat1':
			$('#statdescription').html(s1)
			break
		case 'stat2':
			$('#statdescription').html(s2)
			break
		case 'stat3':
			$('#statdescription').html(s3)
			break
		case 'stat4':
			$('#statdescription').html(s4)
			break
		case 'stat5':
			$('#statdescription').html(s5)
			break
	}

}
