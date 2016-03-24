
$(document).ready(function() {
    var request_view = '/llamalandmine/handle_requests/';

    $(".accept_request").click(function(){
       handle_item(request_view, $(this).attr('name'), "True");
    });

    $(".decline_request").click(function() {
        handle_item(request_view, $(this).attr('name'), "");
    });

    var challenge_view = '/llamalandmine/handle_challenges/';

    $(".accept_challenge").click(function(){
        handle_item(challenge_view, $(this).attr('name'), "True");
    });

    $(".decline_challenge").click(function() {
        handle_item(challenge_view, $(this).attr('name'), "");
    });

    $(document).popover({ selector: '[data-toggle="popover"]' });
});

function handle_item(view, item, accept){

    var data = {item: item, accept: accept};
    var action = function() {
        location.reload(true);
    };

    post_request_handler(view, data, action);
}