function expandGlobalNav(){
  //expand
  if ($('#nav_expand').attr('value') == 'contracted'){
    console.log('expanding nav')
    $('#nav_container').animate({top:"0"}, 350, function(){$('#nav_expand').attr('value','expanded')})
  } else{ //contract
    console.log('contracting nav')
    $('#nav_container').animate({top:"-100vh"}, 350, function(){$('#nav_expand').attr('value','contracted')})
  }
}
function expandPagenav(){
    $('#pagenav').animate({
          top: '40px',
      }, 300, function(){
        $('#pagenav_expand').attr('onclick', 'collapsePagenav()')
      });
}
function collapsePagenav(i){
  $('#pagenav').animate({
        top: '-50vh',
    }, 300, function(){
      $('#pagenav_expand').attr('onclick', 'expandPagenav()')
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
    if(id=='top'){scrollpos = 0}else{
    scrollpos = $("#"+id).offset().top - 20;}
    $('html, body').animate({
          scrollTop: scrollpos
      }, 500);
  }
}

$( document ).ready(function() {
    implode();
    $('#pagenav_expand').attr('onclick', 'expandPagenav()');
});



