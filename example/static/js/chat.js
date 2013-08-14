/*
 NOTE, you need to pass in ROOM_ID and NICKNAME as variables ot this script.
*/

var chatsocket = io.connect("/chat");


function join_room(room_id, nickname){    
    chatsocket.emit('join', room_id, nickname);
}

chatsocket.on('connect', function () {     
    $('#chat').addClass('connected');
    //chatsocket.emit('join', ROOM_ID, NICKNAME);
});

chatsocket.on('announcement', function (msg) {
    $('#lines').append($('<p>').append($('<em>').text(msg)));
});

chatsocket.on('nicknames', function (nicknames) {
    $('#nicknames').empty().append($('<span>Online: </span>'));
    for (var i in nicknames) {
        $('#nicknames').append($('<b>').text(nicknames[i]));
    }
});

chatsocket.on('msg_to_room', message);

chatsocket.on('reconnect', function () {
    $('#lines').remove();
    message('System', 'Reconnected to the server');
});

chatsocket.on('reconnecting', function () {
    message('System', 'Attempting to re-connect to the server');
});

chatsocket.on('error', function (e) {
    message('System [error]', e ? e : 'A unknown error occurred');
});

function message (from, msg) {
    $('#lines').append($('<p>').append($('<b>').text(from), msg));
}

// DOM manipulation
$(function () {
    // $('#set-nickname').submit(function (ev) {
    //     chatsocket.emit('nickname', $('#nick').val(), function (set) {
    //         if (set) {
    //             clear();
    //             return $('#chat').addClass('nickname-set');
    //         }
    //         $('#nickname-err').css('visibility', 'visible');
    //     });
    //     return false;
    // });

    $('#send-message').submit(function () {
        message('me', $('#message').val());
        chatsocket.emit('user message', $('#message').val());
        clear();
        $('#lines').get(0).scrollTop = 10000000;
        return false;
    });

    function clear () {
        $('#message').val('').focus();
    };
});
