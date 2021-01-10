var room;
var a= 1;

$(document).ready(function(){

    function show_hide(){
        if(a == 1){
            $('#response').css("display","inline");
            $('#cancel').css("display","inline");
            $('#submit').css("display","inline");
            $('#reply').css("display","none");
            a = 0;
        }
    
        else{
            $('#response').css("display","none");
            $('#cancel').css("display","none");
            $('#submit').css("display","none");
            $('#reply').css("display","inline");
            a = 1;
        }
    }


    $('#reply').on('click', show_hide);
    $('#cancel').on('click', show_hide);
    $('#submit').on('click', show_hide);

    // connects to a socket
    socket = io.connect('http://127.0.0.1:5000')

    // emits the join room event which is used to add the user to a room in the backend
    socket.emit('join-room', window.location.href);
    
    socket.on('connect',function(){
        console.log('connected');
    });

    socket.on('joined-room', function(data){
        room = data;
    });

    $("#submit").on('click', function(e){
        e.preventDefault();
        socket.emit('replied',{ 'thread_content':$('#response').val(), 'thread_room':room });
        $('#response').val(' ');
    });

    socket.on('replied',function(data){
        $('.thread-container').append(
            `<div class="comment">
                <div class="user">${data.user}</div>
                <div class="date">${data.date}</div>
                <div class="content">
                    <h5>${data.content}</h5>
                </div>
            </div>`);
    });
    
});