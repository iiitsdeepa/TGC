function expandNav(){
		$('#nav_container').animate({
	        top: '0',
	    }, 500, function(){
	    	$('#nav_expand').attr('onclick', 'collapseNav()')
	    	console.log('now collapsable')
	    });
	    $.scrollLock();
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
    $.scrollLock();
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

$.scrollLock = ( function scrollLockSimple(){
	var locked   = false;
	var $body;
	var previous;

	function lock(){
	  if( !$body ){
	    $body = $( 'body' );
	  }
	  
	  previous = $body.css( 'overflow' );
		
	  $body.css( 'overflow', 'hidden' );

	  locked = true;
	}

	function unlock(){
	  $body.css( 'overflow', previous );

	  locked = false;
	}

	return function scrollLock( on ) {
		// If an argument is passed, lock or unlock depending on truthiness
		if( arguments.length ) {
			if( on ) {
				lock();
			}
			else {
				unlock();
			}
		}
		// Otherwise, toggle
		else {
			if( locked ){
				unlock();
			}
			else {
				lock();
			}
		}
	};
}() );