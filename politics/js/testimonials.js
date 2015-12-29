function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}


// A $( document ).ready() block.
$( document ).ready(function() {
    tm = getParameterByName('tm')
    if (tm=='ss'||tm=='js'||tm=='da'||tm=='aw'||tm=='kk'||tm=='tc'){
		$('#amth').css('display','none')
		$('#'+tm).css('display','block')
	}
});