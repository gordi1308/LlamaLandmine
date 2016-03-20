
$(document).ready(function() {
    $(".accept").click(function(){
       handle_request($(this).attr('name'), "True");
    });

    $(".decline").click(function() {
        handle_request($(this).attr('name'), "");
    });
});

function handle_request(from, accept){

    function getCookie(name) {
        var cookieValue = null;

        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var csrftoken = getCookie('csrftoken');

    $.ajax({
        type: 'POST',
        url: '/llamalandmine/handle_requests/',
        data: {
            from: from,
            accept: accept,
            csrfmiddlewaretoken: csrftoken
        },
        success: function() {
            location.reload(true);
        }
    });
}
