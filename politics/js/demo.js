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

function showThird(){
	$('#demo_content').css('width', '1200px')
	$('.findform_wrapper').css('width', '1200px')
	$('#reps_container').css('width', '1030px')
	$('#replinks_wrapper').css('width', '1050px')
	$('.rep_wrapper').css('width', '33%')
	$('#last_replink').css('display', 'flex')
	$('#js_wrapper').css('display', 'block')
}

function useLocation() {
	console.log('using location')
    navigator.geolocation.getCurrentPosition(gotGPS);
}
function gotGPS(position) {
	lat = position.coords.latitude;
	lng = position.coords.longitude;
	console.log(lat+' '+lng)
	$.post('/home', {lat: lat, lng: lng}, function(data){
		window.location.replace("/home?district="+data);
	});
}
function useAddress(){
	street = document.getElementById('address').value;
	state = document.getElementById('state').value;
	city = document.getElementById('city').value;
	address = street+' '+city+' '+state
	$.post('/home', {address: address}, function(data){
		window.location.replace("/home?district="+data);
	});
}

function setState(){
	state=$('#page-data').val()
	if (state == 'found-district'){
		console.log("Inside")
		showThird();
	}
}

function startPosition(){
	scrollTo('demo_wrapper');
}

$( document ).ready(function() {
	setState();
	startPosition();
	slider(1,'topic','','flex');
});