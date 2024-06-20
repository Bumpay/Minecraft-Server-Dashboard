$(document).ready(function () {

    // Redirect to dashboard if already logged in
    if (localStorage.getItem('jwtToken') && window.location.pathname === '/login') {
        window.location.href = '/dashboard';
    }

    // Redirect to login if not logged in and trying to access dashboard
    if (!localStorage.getItem('jwtToken') && window.location.pathname === '/dashboard') {
        window.location.href = '/login';
    }

    // Login
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
                window.location.href = '/dashboard';
            },
            error: function(xhr, status, error) {
                $('#message').text('Error: ' + xhr.responseJSON.message);
            }
        });
    });

    // Handle logout button click
    $('#logoutBtn').click(function() {
        localStorage.removeItem('jwtToken');
        window.location.href = '/login';
    });

    function updateServerStats() {
        var token = localStorage.getItem('jwtToken');
        if(!token) {
            $('#message').text('No token found. Please login first');
            return;
        }

        $.ajax({
            type: 'GET',
            url: '/api/stats',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            success: function (response) {
                $('#serverStatus').text('Server Status: ' + response.online);
                $('#playersOnline').text('' + response.current_players + ' of ' + response.max_players + ' players online');
                $('#playerList').text('Players: ' + response.players);
            },
            error: function (xhr, status, error) {
                $('#message').text('Error fetching server status: ' + xhr.responseJSON.message);
            }
        });
    }

    // Fetch server resource usage
    function updateServerResources() {
        var token = localStorage.getItem('jwtToken');
        if(!token) {
            $('#message').text('No token found. Please login first');
            return;
        }

        $.ajax({
            type: 'GET',
            url: '/api/server/resources',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            success: function(response) {
                $('#cpuUsage').text('CPU Usage: ' + response.cpu_usage);
                $('#memoryUsage').text('Memory Usage: ' + response.memory_usage);
                $('#memoryLimit').text('Memory Limit: ' + response.memory_limit);
                $('#memoryPercent').text('Memory Percent: ' + response.memory_percent);
            },
            error: function(xhr, status, error) {
                $('#message').text('Error fetching server resources: ' + xhr.responseJSON.message);
            }
        });
    }

    // Start regular updates for server resources
    function startResourceUpdates() {
        updateServerResources();
        updateServerStats();
        setInterval(updateServerResources, 5000);
    }

    // Check if token exists and start updates if logged in
    if (localStorage.getItem('jwtToken') && window.location.pathname === '/dashboard') {
        console.log('Start fetching');
        startResourceUpdates();
    }
});
