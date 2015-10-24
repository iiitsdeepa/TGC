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
	$('.mexp').css('background-color','orange');
	$('.nav_option').attr('value','contracted');
	console.log('all contracted')
}
function submarine(li, bt){
	console.log(li + ' is ' + $('#'+li).attr('value'));
	//expand the subnav
	if ($('#'+li).attr('value') == 'contracted'){
		implode();
		$('#'+bt).css('background-color','red');
		$('#'+li).attr('value', 'expanded');
		console.log(li+' now expanded')
	}
	//contract the subnav
	else{
		console.log('in the else')
		$('#'+li).attr('value', 'contracted');
		implode();
	}

};


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