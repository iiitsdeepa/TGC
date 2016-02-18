"use strict"

function validDistrict(str){
  var re = '^[A-Z]{2}:[0-9]{1,2}';
  var test = str.match(re)
  return test
}

function rightEntry(id){
  var w =  $('#'+id).css('display','block')
  var w =  $('#'+id).width()
  $('#'+id).css('right',-w)
  $('#'+id).animate({
        right:'0'
        }, 150);
}

function fadeIn(id){
  $('#'+id).css('display','block')
  $('#'+id).css('opacity','0')
  $('#'+id).animate({
        opacity: "1"
        }, 500);
}

function scroller(id,classname){
  $('.'+classname).each(function(index){
    $(this).css('display','none')
  })
  $('#'+id).css('display','block')
  fadeIn(id)
}

function showHide(classname, index, hide){
  console.log(classname, index, hide)
  if(hide != '-1'){
      $('.'+classname).each(function(i){
        if(i == index){
          $(this).css('display','block')
          var others = $(this).attr('value')
          console.log(i, $(this).attr('id'), others)
          fadeIn($(this).attr('id'))
          fadeIn(others)
        }else{
          $(this).css('display','none')
        }
    })
  }
}

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
    var scrollpos = $("#"+id).offset().top - 20;}
    $('html, body').animate({
          scrollTop: scrollpos
      }, 500);
  }
}

function getParameterByName(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}

$( document ).ready(function() {
    implode();
    $('#pagenav_expand').attr('onclick', 'expandPagenav()');
});



