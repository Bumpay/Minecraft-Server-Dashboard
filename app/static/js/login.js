$(document).ready(function () {

    $('#loginForm').submit(function (event) {
        event.preventDefault();

        var username = $('#username').val();
        var password = $('#password').val();
        var credentials = btoa(username + ':' + password);

        $.ajax({
            type: 'POST',
            url: '/login',
            headers: {
                'Authorization': 'Basic ' + credentials
            },
            success: function (response) {
                var token = response.token;
                localStorage.setItem('jwtToken', token);
                $('#message').text('Login successfull! Token received.');
                $('#loginForm').hide();
                $('#content').show();
            },
            error: function(xhr, status, error) {
                $('#message').text('Error: ' + xhr.responseJSON.message);
            }
        });
    });

    $('#logoutBtn').click(function() {
        localStorage.removeItem('jwtToken');
        $('#loginForm').show();
        $('#content').hide();
        $('#message').text('');
        $('#username').val('');
        $('#password').val('');
    });
});