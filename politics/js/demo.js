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

function inputRepData(data){
	j = JSON.parse(data)
	if ($('#reps_slider').attr('value') == 'leaders'){
		$('#hrpic').css('background', 'url(/images/headshots/'+j.spthpic+'.png)')
		$('#sspic').css('background', 'url(/images/headshots/'+j.smjlpic+'.png)')
		$('.reppic_wrapper').css('background-size', '100%')
	}
	else {
		$('#hrpic').css('background', 'url(/images/headshots/'+j.hrpic+'.png)')
		$('#sspic').css('background', 'url(/images/headshots/'+j.sspic+'.png)')
		$('#jspic').css('background', 'url(/images/headshots/'+j.jspic+'.png)')
		$('.reppic_wrapper').css('background-size', '100%')
	}
	//update names
	$('#hrname').html(j.hrname)
	$('#ssname').html(j.ssname)
	$('#jsname').html(j.jsname)
	//update ployalty
	$('#ployalty .hrstat').html(j.hrployalty+'%')
	$('#ployalty .ssstat').html(j.ssployalty+'%')
	$('#ployalty .jsstat').html(j.jsployalty+'%')
}
function useLocation() {
	console.log('using location')
    navigator.geolocation.getCurrentPosition(gotGPS);
}
function gotGPS(position) {
    lat = position.coords.latitude;
    lng = position.coords.longitude;
    $.post('/mreps', {lat: lat, lng: lng}, function(data){
    	j = JSON.parse(data)
    	$('#reps_slider').attr('value', j.district)
    	$('#js_wrapper').css('display', 'block')
    	$('.jsstat').css('display', 'block')
        inputRepData(data)
    });
}
function useAddress(){
	street = document.getElementById('address').value;
	state = document.getElementById('state').value;
	city = document.getElementById('city').value;
	address = street+' '+city+' '+state
	$.post('/mreps', {address: address}, function(data){
    	j = JSON.parse(data)
    	$('#reps_slider').attr('value', j.district)
    	$('#js_wrapper').css('display', 'block')
    	$('.jsstat').css('display', 'td')
        inputRepData(data)
    });
}

$( document ).ready(function() {
    $.post('/mreps', {demo: 'yes'}, function(data){
  		inputRepData(data)
    });
});