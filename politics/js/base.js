function expandNav(){
		$('#nav_container').animate({
	        top: '0',
	    }, 500, function(){
	    	$('#nav_expand').attr('onclick', 'collapseNav()')
	    	console.log('now collapsable')
	    });
	    $.scrollLock();
}

function collapseNav(){
	h = -1 * $('nav_container').height()
	$('#nav_container').animate({
        top: '-100vh',
    }, 500, function(){
    	$('#nav_expand').attr('onclick', 'expandNav()')
    	$('#badge').css('display', '');
    });
    $.scrollLock();
}

function submarine(){
	console.log($(this).parent())

}
function hotair(){
	
}
function implode(){
	
}

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