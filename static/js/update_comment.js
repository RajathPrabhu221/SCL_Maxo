$(document).ready(function(){

    socket = io.connect('http://127.0.0.1:5000')

    socket.on('connect',function(){
        console.log('connected');
    })

    $("#comment_form").on('submit', function(e){
        e.preventDefault();
        socket.emit('commented', $('#comment_content').val());
        $('#comment_content').val(' ');
    });
});