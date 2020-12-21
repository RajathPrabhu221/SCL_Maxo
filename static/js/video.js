const connect_room_btn = document.getElementById('connection');
const video_element = document.getElementById('video');
const audio_btn = document.getElementById('audio_btn');
const video_btn = document.getElementById('video_btn');
var username = "Mr. Robot";
const roomname = "Daily-Standup";
var video_connected = false; // keeps track of the status of video of local participant(i.e is on/off)
var audio_connected = false; // keeps track of the status of audio of local participant(i.e is on/off)
var connected = false; // keeps track of the status of connection of participant to the room (i.e if the participant is connected to the room or not)
var room;

// publishes the media of the local participant
function addLocalVideo() {
    Twilio.Video.createLocalVideoTrack().then(track => {
        let trackElement = track.attach();
        video_element.appendChild(trackElement);
    });
}

// handles the event of the user clicking the join/leave meet button
function connectButtonHandler(event) {
    event.preventDefault();
    if (!connected) {
        connect(username, roomname).then(() => {
          console.log("connected");
        }).catch(() => {
            alert('Connection failed. Please grant access to your webcam?');
        });
    }
    else {
        disconnect();
    }
}

function connect(username, roomname) {
    let promise = new Promise((resolve, reject) => {
        // gets the token corresponding to the local participant from the back end
        let data;
        fetch('/gen_token', {
            method: 'POST',
            body: JSON.stringify({'username': username, 'roomname': roomname}) // sends username and roomname as json to the backend
        }).then(res => res.json()).then(_data => { // _data contains the token from the backend
            data = _data;
            // uses the token to connect to the room
            return Twilio.Video.connect(data.token, {name:roomname});
        }).then(_room => {
            addLocalVideo();
            room = _room;
            // for each participant that is already connected call the function participantConnected on it
            room.participants.forEach(participantConnected);
            // attach an event listener to the room which notifies, if a participant connects at some point during the meet
            room.on('participantConnected', participantConnected);
            // attach an event listener to the room that notifies, if a participant leaves the call
            room.on('participantDisconnected', participantDisconnected);
            connected = true;
            video_connected = true;
            audio_connected = true;
            // on connecting change the buttons function from joining the meet to disconnecting from it
            connect_room_btn.innerHTML = 'leave meet';
            // resolves the promise on successfully connecting to the room
            resolve();
        }).catch(e => {
            // if there is any error in the due course of the promise it is caught
            console.log(e);
            // promise is rejected
            reject();
        });
    });
    return promise;
}

function participantConnected(participant) {
    // creates a sperate div for each participant and assign its id the name of the participant
    let participant_div = document.createElement('div');
    participant_div.setAttribute('id', participant.sid);
    participant_div.setAttribute('class', 'participant');

    // to the above created div attach another div which will hold the media from the participant(i.e video and audio elements)
    let tracks_div = document.createElement('div');
    participant_div.appendChild(tracks_div);

    // attaches it with a div that holds the name of the participant so that other participants can see the name
    let labelDiv = document.createElement('div');
    labelDiv.setAttribute('class', 'label');
    labelDiv.innerHTML = participant.identity;
    participant_div.appendChild(labelDiv);

    // the div created above is finally attached to the main meet call div which will be visible to the participant
    video_element.appendChild(participant_div);

    // loops through all the participants in the room and checks if each one of them has either published their video or audio
    participant.tracks.forEach(publication => {
        // if the participant has published either audio or video we attach this to the participant div that we created above
        if (publication.isSubscribed)
            trackSubscribed(tracks_div, publication.track);
    });
    // attaches an event listener to each particpant so that if a participant eventually publishes his media it can also be added to the div corresponding to that participant
    participant.on('trackSubscribed', track => trackSubscribed(tracks_div, track));
    
}

// handles attaching of all the media elements published by the participants
function trackSubscribed(div, track) {
    // get the media element published by the participant
    let trackElement = track.attach();
    // set its id as sid of the track which will be useful when a particpant decides to unpublish it
    trackElement.setAttribute('id', track.sid);
    // append it to the div element of the participant
    div.appendChild(trackElement);
  
    //adding some important event listeners
    // add event listeners that listen for the event that these media elements are unpublished by remote participants
    track.on('disabled',track_disable);
    // add an event listener that listens for the event which is trigerred back when these media elements are republished by remote participants
    track.on('enabled',track_enable);
}

// handles enabling of the media by remote participants
function track_enable(track){
    // the track corresponding to the media is enables
    document.getElementById(track.sid).style.display = "block";
}

// handles the unpublishing of the media by remote participants
function track_disable(track) {
    // the track corresponding to the media that is disabled is disabled
    document.getElementById(track.sid).style.display = "none";
}

// handles disconnecting of the remote particpants
function participantDisconnected(participant) {
    // the div corresponding to the remote participant is removed
    document.getElementById(participant.sid).remove();
}

// handles the toggling of audio by local participant
function audio_handler(){
    // handles the case when the user is already sharing his audio and wants to disable it
    if (audio_connected)
    {
        room.localParticipant.audioTracks.forEach(publication => {
            publication.track.disable();
      });
        audio_btn.innerHTML = "connect audio";
    }
    // handles the case when user has disabled the video and wants to  enable it
    else
    {
        room.localParticipant.audioTracks.forEach(publication => {
            publication.track.enable();
          });
        audio_btn.innerHTML = "disconnect audio";
    }
    audio_connected = !audio_connected;
}

// handles toggling of video by local participant
function video_handler(){
    // handles the case when the user is already sharing his video and wants to disable it
    if (video_connected)
    {
        room.localParticipant.videoTracks.forEach(publication => {
            publication.track.disable();
        });
      video_btn.innerHTML = "connect video";
    }
    // handles the case when user has disabled the video and wants to  enable it
    else
    {
        room.localParticipant.videoTracks.forEach(publication => {
            publication.track.enable();
        });
        video_btn.innerHTML = "disconnect video";
    }
    video_connected = !video_connected;
}

// handles disconnecting of local participant
function disconnect() {
    //disconnects from the room
    room.disconnect();
    // removes the entire div of the meet
    video_element.remove();
    connected = false;
    // switches the function of button from leaving meet to joining
    connect_room_btn.innerHTML = 'join meet';
}

connect_room_btn.addEventListener('click',connectButtonHandler);
audio_btn.addEventListener('click',audio_handler);
video_btn.addEventListener('click',video_handler);