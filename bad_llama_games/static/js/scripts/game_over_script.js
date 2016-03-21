
$(document).ready(function(){

    $("#challenge").click(function(){

        var input = $("#friend_name").val();
        var view = '/llamalandmine/send_challenge/';
        var data = {to: input};

        var action = function(response) {
            var valid = JSON.parse(response);
            var challenge_div = $("#challenge_div");
            if(valid){
                challenge_div.html("Request sent!");
            }
            else{
                alert("You're not friend with " + input);
                input.val("");
            }
        };

        post_request_handler(view, data, action);
   });
});