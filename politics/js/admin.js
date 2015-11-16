   function submitSign() {
        document.getElementById("subbutton").disabled=true;
        setTimeout('document.getElementById("subbutton").disabled=false;',1200);
        username = document.getElementById('username').value;
        email = document.getElementById('email').value;
        password = document.getElementById('password').value;
        confirmpass = document.getElementById('confirmpass').value;
        error = 0

        if(username.length < 6){ //test username
          unameerror = 'invalid username (> 6 characters)'
          console.log(unameerror)
          error = 1
        }
        if(!/(.+)@(.+){2,}\.(.+){2,}/.test(email)){ //test email
          emailerror = 'invalid email'
          console.log(emailerror)
          error = 1
        }
        if(password.length < 6){ //test password length
          pwerror = 'invalid password (> 6 characters)'
          console.log(pwerror)
          error = 1
        }
        if(password != confirmpass){ //test password match
          pwerror = 'passwords don\'t match'
          console.log(pwerror)
          error = 1
        }

        if (error != 1){
          $.post('/signup',{username: username, email: email, password: password} , function(data){
            console.log(data)
          });
        }

      }

function gateway(){
  secret = document.getElementById('secret').value;
  $.post('/admin', {secret: secret}, function(data){
    console.log(data)
    if (data == 'freedom'){
      $('#gate').css('display', 'none')
    }
  });
}