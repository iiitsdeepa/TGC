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
	s6 = 'This is the text for stat 5'
	s7 = 'This is the text for stat 5'
	s8 = ''

	switch (id){
		case 'head1':
			$('#statdescription').html(s1)
			break
		case 'head2':
			$('#statdescription').html(s2)
			break
		case 'head3':
			$('#statdescription').html(s3)
			break
		case 'head4':
			$('#statdescription').html(s4)
			break
		case 'head5':
			$('#statdescription').html(s5)
			break
		default:
			$('#statdescription').html(s8)
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

function loadStats(){
	$('#change_selector_wrapper').css('display','inline')
}

function cancelStats(){
	$('#change_selector_wrapper').css('animation-name','change_animation3')
	$('#change_checkbox_wrapper').css('animation-name','change_animation4')
	$('#change_checkbox_wrapper').css('animation-duration','500ms')
	$('.change_checkbox').css('animation-name','change_animation4')
	$('.change_checkbox').css('animation-duration','500ms')
	$('.change-check').css('animation-name','change_animation4')
	$('.change-check').css('animation-duration','500ms')
	$('.change_header').css('animation-name','change_animation4')
	$('.change_header').css('animation-duration','500ms')
	$('#change_submit_wrapper').css('animation-name','change_animation4')
	$('#change_submit_wrapper').css('animation-duration','500ms')
	$('#change_submit_button').css('animation-name','change_animation4')
	$('#change_submit_button').css('animation-duration','500ms')
	$('#change_cancel_button').css('animation-name','change_animation4')
	$('#change_cancel_button').css('animation-duration','500ms')
	window.setTimeout(cancelpartB,450);
}
function cancelpartB(){
	$('#change_selector_wrapper').css('display','none')
	$('#change_selector_wrapper').css('animation-name','change_animation1')
	$('#change_checkbox_wrapper').css('animation-name','change_animation2')
	$('#change_checkbox_wrapper').css('animation-duration','1s')
	$('.change_checkbox').css('animation-name','change_animation2')
	$('.change_checkbox').css('animation-duration','1s')
	$('.change-check').css('animation-name','change_animation2')
	$('.change-check').css('animation-duration','1s')
	$('.change_header').css('animation-name','change_animation2')
	$('.change_header').css('animation-duration','1s')
	$('#change_submit_wrapper').css('animation-name','change_animation2')
	$('#change_submit_wrapper').css('animation-duration','1s')
	$('#change_submit_button').css('animation-name','change_animation2')
	$('#change_submit_button').css('animation-duration','1s')
	$('#change_cancel_button').css('animation-name','change_animation2')
	$('#change_cancel_button').css('animation-duration','1s')
}

function getQueryParams(qs) {
    qs = qs.split('+').join(' ');

    var params = {},
        tokens,
        re = /[?&]?([^=]+)=([^&]*)/g;

    while (tokens = re.exec(qs)) {
        params[decodeURIComponent(tokens[1])] = decodeURIComponent(tokens[2]);
    }

    return params;
}

//var query = getQueryParams(document.location.search);
//alert(query.foo);

function submitStats(){
	var checkedValue = new String(''); 
	var inputElements = document.getElementsByClassName('leg-stats');
	var distparams = getQueryParams(document.location.search);
	for(var i=0; inputElements[i]; ++i){
		if(inputElements[i].checked){
			checkedValue = checkedValue + inputElements[i].value + ',';
		}
	}
	checkedValue = checkedValue.substring(0,checkedValue.lastIndexOf(','));
	$('#change_selector_wrapper').css('display','none')
	if(distparams.district == undefined){
		if (checkedValue == '') {
			window.location.replace("/homes=reps&");
		} else {
			window.location.replace("/home?s=reps&stats="+checkedValue);
		}
	} else if (checkedValue == '') {
		window.location.replace("/home?s=reps&district="+distparams.district);
	} else {
		window.location.replace("/home?s=reps&district="+distparams.district+"&stats="+checkedValue);
	}
}

function useLocation() {
	console.log('using location')
    navigator.geolocation.getCurrentPosition(gotGPS);
}
function gotGPS(position) {
	lat = position.coords.latitude;
	lng = position.coords.longitude;
	var distparams = getQueryParams(document.location.search);
	if (distparams.stats == undefined){
		$.post('/home', {lat: lat, lng: lng}, function(data){
			window.location.replace("/home?s=reps&district="+data);
		});
	} else {
		$.post('/home', {lat: lat, lng: lng}, function(data){
			window.location.replace("/home?s=reps&district="+data+"&stats="+distparams.stats);
		});
	}
}
function useAddress(){
	street = document.getElementById('address').value;
	state = document.getElementById('state').value;
	city = document.getElementById('city').value;
	address = street+' '+city+' '+state
	var distparams = getQueryParams(document.location.search);
	if (distparams.stats == undefined){
		$.post('/home', {address: address}, function(data){
			window.location.replace("/home?s=reps&district="+data);
		});
	} else {
		$.post('/home', {address: address}, function(data){
			window.location.replace("/home?s=reps&district="+data+"&stats="+distparams.stats);
		});
	}
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