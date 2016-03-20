
$(document).ready(function() {
    $(".accept").click(function(){
       handle_request($(this).attr('name'), "True");
    });

    $(".decline").click(function() {
        handle_request($(this).attr('name'), "");
    });
});

function handle_request(from, accept){

    var view = '/llamalandmine/handle_requests/';
    var data = {from: from, accept: accept};
    var action = function() {
        location.reload(true);
    };

    post_request_handler(view, data, action);
}
