function alphaExpand(a, t){
	//expand it
	if ($(t).attr('value') == 'contracted'){
		$('#'+a).animate({
    		height: "170px"
  			}, 200, function() {
    			$(t).attr('value', 'expanded')
  			});
	}
	//contract it
	else{
		$('#'+a).animate({
    		height: "50px"
  			}, 200, function() {
    			$(t).attr('value', 'contracted')
  			});
	}
}

function alphaLogin(){
  document.getElementById("subbutton").disabled=true;
  setTimeout('document.getElementById("subbutton").disabled=false;',1200);
	username = document.getElementById('username').value;
  password = document.getElementById("password").value;
	$.post('/login', {username: username, password: password}, function(data){
    if (data == 'in'){
      
    }
  });
}

function showPopup(popupid){
  $('#'+popupid).css('display', 'block');
  $('#popuplayer').css('display', 'block');
  //$("#popuplayer").attr("onclick", 'hidePopup(\'' + popupid + '\')');
}

function hidePopup(popupid){
  $('#'+popupid).css('display', 'none');
  $('#popuplayer').css('display', 'none');
}

function submitSign() {
  document.getElementById("subbutton").disabled=true;
  setTimeout('document.getElementById("subbutton").disabled=false;',1200);
  email = document.getElementById('nemail').value;
  console.log(email)
  $.post('/newsletter', {email: email}, function(data){
    console.log(data)
  });
}

function scrollTo(id){
  if (id){
    scrollpos = $("#"+id).offset().top - 100;
    console.log($("#"+id).offset().top)
    $('html, body').animate({
          scrollTop: scrollpos
      }, 500);
  }
}