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
