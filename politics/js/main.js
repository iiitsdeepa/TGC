//-------------GLOBAL VARIABLES------------------
var CARDSSHOWN = 0;

//-------Returns the type of device, M, ML, T, or D
function screenType(){
    vw = $(window).width();
    type = 'M';
    CARDSSHOWN = 1;
    if(vw > 420 && vw < 750 && window.innerHeight < window.innerWidth){
        type = 'ML';
        CARDSSHOWN = 1;
    } else if (vw > 420 && vw < 960){ 
        type = 'T';
        CARDSSHOWN = 1;
    }
    else if (vw >= 960){ type = 'D'}

    return type
}

function touchDevice() {
 return (('ontouchstart' in window)
      || (navigator.MaxTouchPoints > 0)
      || (navigator.msMaxTouchPoints > 0));
}

function showCardButtons() {
    $('.card_button').css('display', 'block');
    $('#gc_benefits').css('overflow', 'hidden');
    console.log('showing cards');
}

//These functions ensure that content stays optimized when users change viewport size
function mobile() {
    optimizeCards();
}

function middle() {
    console.log('middle')
    landscapeCards()
    vw = $(window).width();
    console.log(vw)
    if ( $('#benefits_constant').html()=='' ){//needs to move content
        $('#gc_benefits').css('left', '0');
        $('.scroller_constant').css('width', '100vw');
        $('#benefits_constant').append($('#benefits_outside').html());
        $('#benefits_outside').html('');
        $('#vst_constant').append($('#vst_outside').html());
        $('#vst_outside').html('');
        $('#findrep').append($('#rep_question').html());
        $('#rep_question').html('');
        if (vw >= 750 || window.innerHeight < window.innerWidth) {
        }
    }
    optimizeCards();
    $('#lcard_button').css('left', '0');
    $('.card_button').css('top', '40vw');
    $('.card_button').css('height', '8vw');
    $('.card_button').css('width', '10vw');
}


function desk() {

    console.log('desktop')
    console.log(CARDSSHOWN)
    if (CARDSSHOWN == 1){
        $('#gc_benefits').css('left', '50vw');
        $('#gc_benefits').css('opacity', '1');
        showCardButtons()
    }
    if ( $('#benefits_constant').html()=='' ){//needs changing
        halfwidthCards();
    }else{ //is good from load
        halfwidthCards();
        $('#benefits_outside').append($('#benefits_constant').html());
        $('#rep_question').append($('#findrep').html());
        $('#findrep').html('');
        $('#benefits_constant').html('');
        $('#vst_outside').append($('#vst_constant').html());
        $('#vst_constant').html('');
        $('.scroller_constant').css('width', '2.5vw');
        $('#benefits_scroller').css('width', '142.5vw');

    }
    optimizeCards();

}

var bounds = [
    {min:0,max:420,func:mobile}, //loads mobile cards
    {min:421,max:959,func:middle}, //loads full width cards
    {min:959,func:desk} //loads half width cards
];

var resizeFn = function(){
    var lastBoundry; // cache the last boundry used
    return function(){
        var width = window.innerWidth;
        var boundry, min, max;
        for(var i=0; i<bounds.length; i++){
            boundry = bounds[i];
            min = boundry.min || Number.MIN_VALUE;
            max = boundry.max || Number.MAX_VALUE;
            if(width > min && width < max 
               && lastBoundry !== boundry){
                lastBoundry = boundry;
                return boundry.func.call(boundry);            
            }
        }
    }
};
$(window).resize(resizeFn());
//==========================================================================================

function cardEntrance(){
    console.log('cardEntrance')
    $('#gc_benefits').animate({
        left: '50vw',
        opacity: '1'
    }, 700, function () {
        CARDSSHOWN = 1;
        showCardButtons()
    });
}

function showSignup (){
    var form_height = $('#signup_form').height();
    console.log(form_height)
    $("#sform_container").animate({
        height: '+=' + form_height
    });
    $("#signup_stuff").animate({
        height: '+=' + form_height
    });
    $('#signup_form').css('color','darkred')
    $('#sbutton').text("Submit")
    $('#sbutton').attr('onclick', 'signupValidate()')
}

function hasWhiteSpace(s) {
  return /\s/g.test(s);
}

function signupValidate() {

    username = document.getElementById('username').value;
    email = document.getElementById("email").value;
    password = document.getElementById("password").value;
    confirm = document.getElementById("confirm_pass").value;

    num_entered_fields = 4;

    //test username
    $('#username').css({'color':'darkred'});
    if (!username) {
        $('#username').val('');
        $('#username').attr('placeholder', 'please enter a username');
        num_entered_fields -= 1;
    } else {
        if (username.length < 6) {
            $('#username').val('');
            $('#username').attr('placeholder', 'must be longer than 6 characters');
            num_entered_fields -= 1;
        } else if (username.length >= 25){
            $('#username').val('');
            $('#username').attr('placeholder', 'can\'t be more than 25 characters');
            num_entered_fields -= 1;
        } else if (hasWhiteSpace(username)) {
            $('#username').val('');
            $('#username').attr('placeholder', 'invalid, no spaces or tabs');
            num_entered_fields -= 1;
        } else {
            $('#username').css({'color':'limegreen'});
        }
    }

    //test email
    $('#email').css({'color':'darkred'});
    if (!email){
        $('#email').val('');
        $('#email').attr('placeholder', 'please enter an email');
        num_entered_fields -= 1;
    } else {
        if (/[\S]+@[\S]+\.[\S]+$/.test(email)){
            $('#email').css({'color':'limegreen'});
        } else {
            $('#email').val('');
            $('#email').attr('placeholder', 'invalid email');
            num_entered_fields -= 1;
        }
    }

    //test passwords
    if (!password) {
        $('#password').val('');
        $('#password').attr('placeholder', 'please enter a password');
        num_entered_fields -= 1;
    }
    if (!confirm) {
        $('#confirm_pass').val('');
        $('#confirm_pass').attr('placeholder', 'please confirm password');
        num_entered_fields -= 1;
    }
    if (password && confirm){
        if (password.length < 6) {
            $('#password').val('');
            $('#confirm_pass').val('');
            $('#password').attr('placeholder', 'must be longer than 6 characters');
        } else {
            if (password == confirm) {
                $('#password').css({'color':'limegreen'});
                $('#confirm_pass').css({'color':'limegreen'});
            } else {
                $('#password').val('');
                $('#password').attr('placeholder', 'your passwords don\'t match');
                $('#confirm_pass').val('');
                num_entered_fields -= 1;
            }
        }
    }

    //all of the local testing is done, to the server!!

    if (num_entered_fields == 4) {
        $.post('/testpage', { username: username, email: email, password: password }, function(data){
            if (data == '1') { //created user and logged in
            } else if (data =='2') { //username taken
                $('#username').val('');
                $('#username').attr('placeholder', 'that username is taken');
            } else if (data == '3') { //email taken
                $('#email').val('');
                $('#email').attr('placeholder', 'that email is taken');
            } else if (data == '4') { //both taken
                $('#username').val('');
                $('#username').attr('placeholder', 'that username is taken');
                $('#email').val('');
                $('#email').attr('placeholder', 'that email is taken');
            }
        });
    }

}

//------------These Functions Expand the find district if a zip has > 1 districts--------------

function zipFormOptimize_M(zip, districts, num_districts){
    console.log(districts);
    $('#findrep').css('height', '140vw');
    $('#map_container').css('display', 'block');
    $('#zip_title').css('font-size', '115%');
    $('#data_note').css('font-weight', 'normal');
    $('#data_note').css('font-size', '85%');
    $('#zip_form').animate({
        left: '3vw',
        width: '94vw',
        height: '120vw',
        margin: '0'
    }, function(){
        initializeMap();
        console.log(zip)
        codeAddress(zip);
    });
}

function zipFormOptimize_D(zip, districts, num_districts){
    console.log(districts);
    $('#stack_question').css('display', 'none');
    $('#findrep').css('top', '10%');
    $('#findrep').css('height', '100%');
    $('#stack_list').css('display', 'none');
    $('#map_container').css('display', 'block');
    $('#zip_form').animate({
        left: '10%',
        width: '80%',
        height: '36vw',
        margin: '0'
    }, function(){
        initializeMap();
        console.log(zip)
        codeAddress(zip);
    });
}


function zipFormOptimize(zip, districts, num_districts){
    type = screenType();
    if (type == 'M' || type == 'T') {
        zipFormOptimize_M(zip, districts, num_districts);
    } else if (type == 'D') {
        zipFormOptimize_D(zip, districts, num_districts);
    }
    $('#use_location').attr('onclick', 'useLocationExpanded()');
    $('#zip_submit').attr('onclick', 'submitLocation()');
    $('#zip_form').attr('onsubmit', 'javascript:submitLocation();return false;');
    var typingTimer;                //timer identifier
    var doneTypingInterval = 500;  //time in ms, 5 second for example
    //on keyup, start the countdown
    $('#zip').keyup(function(){
        clearTimeout(typingTimer);
        typingTimer = setTimeout(geocodeAddress, doneTypingInterval);
    });

    //on keydown, clear the countdown 
    $('#zip').keydown(function(){
        clearTimeout(typingTimer);
    });
}

//===============================================================================================
//------------These functions work the find district form----------------------------------------
function handleZip() {

    zip = document.getElementById('zip').value;
    var regPostalCode = new RegExp("^\\d{5}(-\\d{4})?$");
    if (regPostalCode.test(zip)) {
        console.log('valid zip');
        zipToDistrict(zip);
    } else {
        addressToDistrict(zip);
    }
}

function zipToDistrict(zip) { //sends the json recieved from external api

    $.post('/main', {zip: zip}, function(data){
        json = JSON.parse(data);
        num_districts = json.count;
        if (num_districts == 1) { //only one possible district
            district = json.results[0].state + ':' + json.results[0].district;
            recievedDistrict(district);
        } else { //more than one possible district
            var districts = [];
            for (i = 0; i < num_districts; i++) { 
                district = json.results[i].state + ':' + json.results[i].district;
                districts[i] = district;
            }
            msg = 'There are XXXX districts for that zip code';
            var msg1 = msg.replace('XXXX', num_districts);
            $('#zip_title').text(msg1);
            $('#zip_title').css('font-size', '125%');
            $('#zip').css('color', 'white');
            $('#zip').val('');
            $('#zip').attr('placeholder', 'Enter Address');
            zipFormOptimize(zip, districts, num_districts);
        }
    });
}

function addressToDistrict(address) { //sends form input to server as an address
    var dist_test = new RegExp("^[A-Z]{2}:[0-9]{1,2}$");
    $.post('/main', {address: address}, function(data){
        if (dist_test.test(data)) { //received a valid district
            recievedDistrict(data)
        } else { //did not recieve a valid district from server
            $('#zip_title').text('oops addressToDistrict failed');
        }
    });
}

function recievedDistrict(district) { //runs when a district is recieved from the server and modifies it all
    t = 'You\'re in district XXXX';
    msg = t.replace('XXXX', district);
    $('#zip_title').text(msg);
    $('#zform_elements').css('display', 'none');
    pullCards(district)
}

var geocoder; //To use later
var map; //Your map
var marker; //the marker
function initializeMap() {
    geocoder = new google.maps.Geocoder();
    //Default setup
    var latlng = new google.maps.LatLng(40.7127, 74.0059);
    var myOptions = {
        zoom: 11,
        center: latlng,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        componentRestrictions: {country: "us"}
    }
    map = new google.maps.Map(document.getElementById("map_container"), myOptions);
    marker = new google.maps.Marker({
        map: map,
        draggable: true,
        position: latlng
    });
    google.maps.event.addListener(marker, 'dragend', function(evt){
        var lat = marker.getPosition().lat();
        var lng = marker.getPosition().lng();
    });

}

function codeAddress(address) { //takes an address or zip code and moves the marker
    ret = 0
    geocoder.geocode( { 'address': address}, function(results, status) {
      if (status == google.maps.GeocoderStatus.OK) {
        //Got result, center the map and put it out there
        map.setCenter(results[0].geometry.location);
        marker.setPosition(results[0].geometry.location);
        ret = 1;
      } else {
        ret = -1;
      }
    });
    return ret
}

function geocodeAddress() {
    address = $('#zip').val();
    success = codeAddress(address);
    console.log(success)
    if (success == 1) {
        console.log('SUBMIT TIME!');
    }
}

function showUseLocation() {
    if (navigator.geolocation) {
        $('#use_location').css('display', 'block');
    } else {
        console.log('geolocation impossible');
        $('#use_location').css('display', 'none');
    }
}

function useLocation() {
    navigator.geolocation.getCurrentPosition(gotGPS);
}


function useLocationExpanded() {
    navigator.geolocation.getCurrentPosition(gotGPSExp);
}

function gotGPSExp(position) {
    lat = position.coords.latitude;
    lng = position.coords.longitude;
    submitProminence();
}

function sendLatLng(lat, lng) {
    var dist_test = new RegExp("^[A-Z]{2}:[0-9]{1,2}$");
    $.post('/main', {lat: lat, lng: lng}, function(data){
        if (dist_test.test(data)) { //received a valid district
            recievedDistrict(data)
        } else { //did not recieve a valid district from server
            $('#zip_title').text('oops addressToDistrict failed');
        }
    });
}

function gotGPS(position) {
    lat = position.coords.latitude;
    lng = position.coords.longitude;
    sendLatLng(lat, lng);

}

function submitProminence() { //makes the submit button 
    $('#zip_submit').css('background-color', 'white');
    $('#zip_submit').css('color', 'darkred');
}

function collapseForm() {
    
}

function submitLocation() { //what the submit button calls when the form has been expanded
    console.log('submitLocation');
    lat = marker.getPosition().lat();
    lng = marker.getPosition().lng();
    sendLatLng(lat, lng);
}

//------------------------these functions play a part in the optimization of cards

function cardNavButtons(){
    if (!touchDevice()) {
        $(".card_button").css('display', 'block');
        console.log('!touchDevice');
    } else {
       console.log('touchDevice');
    }
}

function portraitCards(){
    $('#gc_benefits').css('background-color', 'white');
    $('#deck').css('height', '108vw');
    $('#deck').css('width', '285vw');
    $('#deck').css('background-color', 'white');
    $('.cspacer').css('width', '5vw');
    $('.politician_card').css('width', '90vw');
    $('.cprofile_pic').css('height', '95%');
    $('.cbase_content').css('height', '35%');
    $('.cbase_content').css('width', '100%');
    $('.cstat').css('height', '25%');
    $('.cstat').css('width', '100%');
    $('.cside_list').css('position', 'absolute');
    $('.cside_list').css('top', '60%');
    $('.cside_list').css('width', '100%');
    $('.cside_list').css('height', '40%');
    $('.clist_entries').css('columns', '2');
    $('.clist_entries').css('-webkit-columns', '2');
    $('.clist_entries').css('-moz-columns', '2');
    $('.clist_entries').css('text-align', 'center');
    $('.cstat').css('position', 'relative');
}

function landscapeCards(){
    $('#gc_benefits').css('background-color', 'gainsboro');
    $('#deck').css('height', '36vw');
    $('#deck').css('width', '142.5vw');
    $('#deck').css('background-color', 'gainsboro');
    $('.cspacer').css('width', '2.5vw');
    $('.politician_card').css('width', '45vw');
    $('.cprofile_pic').css('height', '70%');
    $('.cbase_content').css('height', '50%');
    $('.cbase_content').css('width', '60%');
    $('.cstat').css('position', 'absolute');
    $('.cstat').css('height', '50%');
    $('.cstat').css('width', '60%');
    $('.cside_list').css('position', 'absolute');
    $('.cside_list').css('top', '0');
    $('.cside_list').css('top', '0');
    $('.cside_list').css('width', '40%');
    $('.cside_list').css('height', '100%');
    $('.clist_entries').css('columns', '1');
    $('.clist_entries').css('-webkit-columns', '1');
    $('.clist_entries').css('-moz-columns', '1');
    $('.clist_entries').css('text-align', 'left');
}

function mobileLandscapeCards(){
    $('#gc_benefits').css('background-color', 'white');
    $('#deck').css('height', '50.625vw');
    $('#deck').css('width', '240vw');
    $('#deck').css('background-color', 'white');
    $('.politician_card').css('width', '70vw');
    $('.cspacer').css('width', '10vw');
}

function halfwidthCards(){
    $('#benefits_scroller').css('width', '145vw');
    $('#bcard_holder').css('width', '142.5vw');
    $('.politician_card').css('width', '45vw')
    $('#deck').css('height', '36vw');
    $('#deck').css('width', '142.5vw');
    $('.cspacer').css('width', '2.5vw');
    $('#lcard_button').css('left', '50vw');
    $('.card_button').css('top', '20vw');
    $('.card_button').css('height', '4vw');
    $('.card_button').css('width', '5vw');
    $('.card_button').css('line-height', '4vw');
}

function fullwidthCards(){
    console.log('fullwidthCards')
    $('#benefits_scroller').css('width', '385vw');
    $('#bcard_holder').css('width', '285vw');
    $('.politician_card').css('width', '90vw')
    $('#deck').css('height', '72vw');
    $('#deck').css('width', '280vw');
    $('.cspacer').css('width', '5vw');
    $('#lcard_button').css('left', '0');
    $('.card_button').css('top', '40vw');
    $('.card_button').css('height', '8vw');
    $('.card_button').css('width', '10vw');
    $('.card_button').css('line-height', '8vw');
}

function colorCards(){
    if ($('#hrcard').hasClass('D')) {
        $('#hrcard').css('background-color', '#000061');
        $('#hrfoot, #hrhead').css('background-color', '#000061');
        $('#hrcontent').css('background-color', 'darkblue')
        $('#hrstat').css('background-color', 'darkblue')
    } else if ($('#hrcard').hasClass('R')) {
        $('#hrcard').css('background-color', '#610000');
        $('#hrfoot, #hrhead').css('background-color', '#610000');
        $('#hrcontent').css('background-color', 'darkred')
        $('#hrstat').css('background-color', 'darkred')
    }

    if ($('#sscard').hasClass('D')) {
        $('#sscard').css('background-color', '#000061');
        $('#ssfoot, #sshead').css('background-color', '#000061');
        $('#sscontent').css('background-color', 'darkblue')
        $('#ssstat').css('background-color', 'darkblue')
    } else if ($('#sscard').hasClass('R')) {
        $('#sscard').css('background-color', '#610000');
        $('#ssfoot, #sshead').css('background-color', '#610000');
        $('#sscontent').css('background-color', 'darkred')
        $('#ssstat').css('background-color', 'darkred')
    }

    if ($('#jscard').hasClass('D')) {
        $('#jscard').css('background-color', '#000061');
        $('#jsfoot, #jshead').css('background-color', '#000061');
        $('#jscontent').css('background-color', 'darkblue')
        $('#jsstat').css('background-color', 'darkblue')
    } else if ($('#jscard').hasClass('R')) {
        $('#jscard').css('background-color', '#610000');
        $('#jsfoot, #jshead').css('background-color', '#610000');
        $('#jscontent').css('background-color', 'darkred')
        $('#jsstat').css('background-color', 'darkred')
    }
}

function optimizeCards(){
    console.log('optimizeCards')
    type = screenType();
    if (type == 'M') {
        portraitCards();
    } else if (type == 'ML'){
        mobileLandscapeCards();
    } else if (type == 'T') {
        fullwidthCards();
    } else {
        halfwidthCards();
    }
    colorCards();
    cardNavButtons();

}

//================================================================================
//-------------------runs the buttons for the cards-------------------------------
function scrollCardsLeft(){
    $('#lcard_button').attr('onclick', '');
    $('#rcard_button').attr('onclick', '');
    //see if on first card
    limit = $('#gc_benefits').offset().left;
    bscroller = $('#benefits_scroller').offset().left;
    csp1 = $('#csp1').offset().left;
    if ( Math.abs(limit - bscroller) < .05 * limit){
        console.log('first card');
        $('#lcard_button').attr('onclick', 'scrollCardsLeft()');
        $('#rcard_button').attr('onclick', 'scrollCardsRight()');
    } else {
        move = bscroller - csp1;
        $('#benefits_scroller').animate({
            left: '-=' + move,
        }, 500, function() {
            $('#lcard_button').attr('onclick', 'scrollCardsLeft()');
            $('#rcard_button').attr('onclick', 'scrollCardsRight()');
        });
        console.log('did the thing')
    }
    
}

function scrollCardsRight(){
    $('#lcard_button').attr('onclick', '');
    $('#rcard_button').attr('onclick', '');
    //if on last card
    limit = $('#gc_benefits').offset()
    csp2 = $('#csp2').offset()
    if ( Math.abs(limit.left - csp2.left) < .05 * $('#gc_benefits').width()){
        console.log('last card')
        $('#lcard_button').attr('onclick', 'scrollCardsLeft()');
        $('#rcard_button').attr('onclick', 'scrollCardsRight()');
    } else {
        bscroller = $('#benefits_scroller').offset().left;
        csp1 = $('#csp1').offset().left;
        move = bscroller - csp1;
        $('#benefits_scroller').animate({
            left: '+=' + move,
        }, 500, function() {
            $('#lcard_button').attr('onclick', 'scrollCardsLeft()');
            $('#rcard_button').attr('onclick', 'scrollCardsRight()');
        });
        console.log('did the thing')
    }
}

//---------these functions pull the cards and get data for the cards--------------

function getHeadShots(district){//puts the headshot where its supposed to be
    var state = district.split(':');
    hrholder = district.replace(':', '_');
    ssholder = state[0] + '_SS';
    jsholder = state[0] + '_JS';
    var template = 'url(\'/images/headshots/XXXX.png\') no-repeat';
    hrcss = template.replace('XXXX', hrholder);
    sscss = template.replace('XXXX', ssholder);
    jscss = template.replace('XXXX', jsholder);
    $('#hrppic').css('background', hrcss);
    $('#hrppic').css('background-size', '100%');
    $('#ssppic').css('background', sscss);
    $('#ssppic').css('background-size', '100%');
    $('#jsppic').css('background', jscss);
    $('#jsppic').css('background-size', '100%');
}

function pullCards(district) {

    vw = $(window).width()
    vh = $(window).height()

    if (!district){//get the cards for the big 3
        console.log('getting big 3 cards')
        $.get('/cards', function(data){
            $('#bcard_holder').html(data);
            optimizeCards();
        });
    } else {
        console.log('getting district cards')
        $.post('/cards', {district: district}, function(data){
            $('#bcard_holder').html(data);
            optimizeCards();
            getHeadShots(district)
        });
    }

}

//-------------------Main: Runs when page is loaded complely-------------------------
$( document ).ready(function() {
    $(window).trigger('resize');
    showUseLocation();
    vw = $(window).width();
    pullCards();
    carholderoffset = $('#gc_benefits').offset();
    triggerheight = carholderoffset.top - ($('#gc_benefits').height());
    type = screenType();
    console.log(type);
    if (type == 'D'){
        scrollposition = $(this).scrollTop();
        //we start off in a place where the cards should already be shown
        if (scrollposition >= triggerheight) {
            console.log('bring in the cards immediately')
            cardEntrance();
            //turn off the scroll stuff
            $(this).off('scroll');
        }
        $(window).on('scroll', function() {
            type = screenType()
            scrollposition = $(this).scrollTop();
            if (scrollposition >= triggerheight && type == 'D') {
                cardEntrance();
                //turn off the scroll stuff
                $(this).off('scroll');
            }
        });
    }
});
