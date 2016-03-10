"use strict"

function drSwitcher(party){
  if($(window).width() < 966){
    console.log(party)
    $('.pc-section-title').each(function(index){
      $(this).css('background','white')
      $(this).css('color','#999999')
    })
    $('.party-column').each(function(index){
      $(this).css('visibility','hidden')
      $(this).css('position','absolute')
    })
    if(party=='.dpc'){
      $('.pc-dem-title').css('background','#00aef3')
      $('.pc-dem-title').css('color','white')
    } else {
      $('.pc-repub-title').css('background','#CC0000')
      $('.pc-repub-title').css('color','white')
    }
    $(party).css('position','relative')
    $(party).css('visibility','visible')
  }
}

function fontAdjust(id, wrapper){
  var tw
  var dw = $(wrapper).width()
  tw = $(id).find('.text-sizer').width()
  var csize
  var diff
  while (tw < (dw - 100)){
    csize = parseInt($(id).find('.text-sizer').css('font-size'))
    var nsize = csize + 1
    $(id).find('.text-sizer').css('font-size',nsize+'px')
    $(id).css('font-size',nsize+'px')
    $(id).css('line-height',nsize+'px')
    tw = $(id).find('.text-sizer').width()
  }
}

function getVisualizationData(vis){
  $.post('/vishandle', {'visualization':vis}, function(data){
    var objJSON = eval("(function(){return " + data + ";})()");
    google.charts.setOnLoadCallback(drawChart(objJSON))
  })
}

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

function fadeIn(id,display){
  $('#'+id).css('display',display)
  $('#'+id).css('visibility','shown')
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
  fadeIn(id, 'block')
}

function slider(index, classname, direction,display){
  var num = 0;
  $('.'+classname).each(function(index){
    $(this).css('display','none')
    num = num + 1;
  });
  var curr = $('#'+classname+'s').attr('value')
  var next
  if (direction=='left'){next = (parseInt(curr)- 1) % num}
  else if (direction == 'right'){ next = (parseInt(curr) + 1) % num}
  else {next = parseInt(curr) % num}
  $('#'+classname+'s').attr('value',(next+(num * 100)))
  fadeIn(classname+'-'+next,display)
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

function tabSwitcher(id, functext){
  $('#display-tab').html('')
  var result = FUNCTIONS[functext]()
  //var curr = $('#display-tab').val()
  var html = $('#'+id).html()
  //$('#display-tab').html(html)
  //$('#display-tab  .tab-content').css('opacity','0')
  //$('#display-tab  .tab-content').animate({
        //opacity: "1"
        //}, 500);
}

function startState(pagetext){
  var tab = getParameterByName('s')
  if (!tab){
    tab = $('.tab').first().attr('id')
  }
  $('#display-tab').attr('value',tab)
  var functext = pagetext + tab
  tabSwitcher(tab, functext)
}

function submitESF() {
  var email = document.getElementById('esfemail').value;
  console.log(email)
  $.post('/esf', {esfemail:email}, function(data){
    if (data == 'success'){
      console.log(data)
      $('.incomp-pre').css('display','none')
      $('.incomp-post').css('display','block')
    }
  });
}

function navShowHide(){
  //expand
  if ($('#nav-container').attr('value') == 'contracted'){
    console.log('expanding nav')
    $('#nav-container').animate({top:"0"}, 350, function(){$('#nav-container').attr('value','expanded')})
  } else{ //contract
    console.log('contracting nav')
    $('#nav-container').animate({top:"-100vh"}, 350, function(){$('#nav-container').attr('value','contracted')})
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



