function expandNav(){
		$('#nav_container').animate({
	        top: '0',
	    }, 500, function(){
	    	$('#nav_expand').attr('onclick', 'collapseNav()')
	    	console.log('now collapsable')
	    });
}

function collapseNav(){
	$('#nav_container').animate({
        top: '-50vh',
    }, 500, function(){
    	$('#nav_expand').attr('onclick', 'expandNav()')
    	$('#badge').css('display', '');
    });
}

$(document).ready(function() {
    console.log( "ready!" );
    optimizeNav();
});