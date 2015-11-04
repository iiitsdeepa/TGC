function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}
function expandNav(){
		$('#nav_container').animate({
	        top: '0',
	    }, 500, function(){
	    	$('#nav_expand').attr('onclick', 'collapseNav()')
	    	console.log('now collapsable')
	    });
}
function collapseNav(i){
	console.log(i)
	h = -1 * $('nav_container').height()
	$('#nav_container').animate({
        top: '-100vh',
    }, 500, function(){
    	$('#nav_expand').attr('onclick', 'expandNav()')
    	$('#badge').css('display', '');
    });
}
function implode(){
	$('.mexp').html('>')
	$('.nav_option').attr('value','contracted');
	$('nav ul li').css('height', '40px')
}
function submarine(li, bt){
	//expand the subnav
	if ($('#'+li).attr('value') == 'contracted'){
		implode();
		$('#'+li).attr('value', 'expanded');
		$('#'+li).css('background-color', '')
		$('#'+bt).html('-')
		$('#'+li).css('height','');
	}
	//contract the subnav
	else{
		$('#'+li).attr('value', 'contracted');
		implode();
	}

};

$( document ).ready(function() {
	implode();
    $('#nav_expand').attr('onclick', 'expandNav()');
});
