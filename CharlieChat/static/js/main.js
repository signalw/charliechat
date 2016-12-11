function disableButton(buttonId) {
    $(buttonId).prop('disabled',true).addClass('disabled-button');
}
function renableButton(buttonId) {
    $(buttonId).prop('disabled',false).removeClass('disabled-button');
}

function resizeMessages() {
    $('#messages').height($(window).height() - $('#queryForm').height())
}

function scrollMessages() {
    var d = $('#messages');
    d.scrollTop(d.prop("scrollHeight"));
}

if (!('webkitSpeechRecognition' in window)) {
    disableButton('#speakInput');
}
else {
    recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;

    recognition.onstart = function() {
        $('#userInputBox').val('');
        disableButton('#speakInput');
    }
    recognition.onresult = function(event) {
        var interim_transcript = '';

        for (var i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            final_transcript += event.results[i][0].transcript;
          } else {
            interim_transcript += event.results[i][0].transcript;
          }
        }
        $('#userInputBox').val(interim_transcript);
    }
    recognition.onerror = function(event) {
        console.log('error!');
    }
    recognition.onend = function(event) {
        renableButton('#speakInput');
        $('#userInputBox').val(final_transcript);
    }
}

$('body').on('click','#speakInput',function() {
    final_transcript = '';
    recognition.start();
});

$(document).ready(function() {
    resizeMessages();
    scrollMessages();
})
$(window).resize(function() {
    resizeMessages();
    scrollMessages();
})