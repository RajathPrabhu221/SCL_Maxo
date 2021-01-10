$(document).ready(function(){

    socket = io.connect('http://127.0.0.1:5000')

    socket.on('connect',function(){
        console.log('connected');
    });

    $("#comment_form").on('submit', function(e){
        e.preventDefault();
        socket.emit('commented', $('#comment_content').val());
        $('#comment_content').val(' ');
    });

    socket.on('commented',function(data){
        $('.comment-container').append(
            `<a href="/reply?comment_id=${data.id}">    
                <div class="comment">
                    <div class="details">
                        <span class="user">
                            <h4>${data.user}</h4>
                        </span>
                        <span class="date">
                            <h6>${data.date}</h6>
                        </span>
                    </div>
                    <hr>
                    <div class="content">
                        <h5>${data.content}</h5>
                    </div>
                </div>
            </a>`);
    });
});