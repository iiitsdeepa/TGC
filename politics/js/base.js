function newTbar(){
	$('#badge').css('height', '50px');
	$('#badge').css('line-height', '50px');
	$('#tablet_titlebar').css('display', 'block');
	$('#tablet_titlebar').css('height', '50px');
	$('#tablet_titlebar').css('background', 'darkred');
}

function getMNav(){
	console.log('getMNav')
	$.post('/nav', function(data){
        $('#nav_container').html(data);
    });
}

function getDNav(){
	$.get('/nav', function(data){
        $('#nav_container').html(data);
    });
}

function mobileNav(){
	console.log('mobileNav');
	newTbar();
	getMNav();
	$('#titlebar').css('display', 'none');
	$('#badge').css('font-size', '16px');


}

function tabletNav(){
	console.log('tabletNav');
	$('#badge').css('font-size', '24px');
	newTbar();
	getDNav();

}

function desktopNav(){
	console.log('desktopNav');
	getDNav();
	$('#nav_container').css('right', '0')
}

function optimizeNav(){
	l = $('#nav_container').width()
	vl = $(window).width()
	console.log(l)
	console.log(vl)
	//mobile
	if (l >= vl){
		mobileNav();
	}
	else if (l <= vl && l > (vl * .85)){tabletNav();}
	else{desktopNav()}
}

function expandNav(){
	$('#nav_container').animate({
        left: '-35vw',
    }, 500, function(){
    	$('#nav_expand').attr('onclick', 'collapseNav()')
    	console.log('now collapsable')
    });
}

function collapseNav(){
	$('#nav_container').animate({
        left: '-100vw',
    }, 500, function(){
    	$('#nav_expand').attr('onclick', 'expandNav()')
    });
}

$(document).ready(function() {
    console.log( "ready!" );
    optimizeNav();
});