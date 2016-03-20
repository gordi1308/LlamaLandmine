
$(document).ready(function() {

    var request_div = $('#requests');
    var id = request_div.attr('data-user-id');
    var username = request_div.attr('data-user-name');

    $.get('/llamalandmine/get_requests/', {id: id}, function (response) {
        var requests = JSON.parse(response);

        $.each(requests, function(index, value) {
            request_div.append("<p>" + value + "</p>");
            request_div.append($("<button/>", {
                id: "accept_" + value,
                text: "Accept",
                click: function() {
                    $.get("/llamalandmine/handle_requests/", {from: value, accept: "True"}, function(response) {
                        location.reload(true);
                    });
                }
            }));
            request_div.append($("<button/>", {
                id: "decline_" + value,
                text: "Decline",
                click: function() {
                    $.get("/llamalandmine/handle_requests/", {from: value, accept: "False"}, function(response) {
                        location.reload(true);
                    });
                }
            }));
        });
    });
});