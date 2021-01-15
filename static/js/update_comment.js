$(document).ready(function(){

    // establishes a socket
    socket = io.connect('http://127.0.0.1:5000')

    // monitors for the event that marks connection to socket
    socket.on('connect',function(){
        console.log('connected');
    });

    // submits the comment to the backend
    $("#comment_form").on('submit', function(e){
        e.preventDefault();
        str = $('#comment_content').val();
        if (!(!str || /^\s*$/.test(str)))
        {
            socket.emit('commented', $('#comment_content').val());
            $('#comment_content').val(' ');
        }
    });

    // updates the page if there are any comments from remote users
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