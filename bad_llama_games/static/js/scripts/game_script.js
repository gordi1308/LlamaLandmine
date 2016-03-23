$(document).ready(function() {

    // Div element containing the game grid
    var grid_div = $('#grid');

    // Do not display context menu when the user right clicks on a cell
    grid_div.attr('oncontextmenu', 'return false;');

    var grid_size = grid_div.attr('data-size');

    // Timer
    var clock = $('#timer');

    var first_click = false;

    $(".grid_btn").mousedown(function (event) {

        // Start the timer when the user clicks for the first time
        if (!first_click) {
            first_click = true;
            clock.timer({
                format: '%M:%S'
            });
        }

        // Get the coordinates of the cell the user clicked on
        var row = $(this).attr('data-row'), column = $(this).attr('data-column');

        switch (event.which) {
            case 1:
                on_left_click($(this), clock, grid_div);
                break;

            case 3:
                // Update number of mines left
                // when the user flags or unflags a cell
                var mines_counter = $('#mines_counter');
                var mines_left = mines_counter.html();
                mines_left = on_right_click($(this), mines_left);
                mines_counter.html(mines_left);
                break;

            default:
                break;
        }
    });
});

// Event when the user left clicks on a the grid
function on_left_click(btn, clock, grid_div) {

    if(btn.val() == "") {
        var row = btn.attr('data-row'), column = btn.attr('data-column');
        // Call the 'get_grid_data' view
        $.get('/llamalandmine/get_grid_data/', {row: row, column: column}, function (response) {
            // Convert the returned data into JSON
            var content = JSON.parse(response);

            var llamas_counter = $('#llamas_counter');

            var level = "" + grid_div.attr('data-level');
            var time_taken = 0;

            // The view returned a list of cells to reveal
            if ($.isArray(content)) {
                $.each(content, function (index, value) {
                    $(".grid_btn[data-row="+value[0]+"][data-column="+value[1]+"]").val(value[2]);
                });
            }
            // The cell contains a mine -> game over -> stop the timer -> get the current time
            else if (content == "M") {
                btn.val("X");

                clock.timer('pause');
                time_taken = clock.data('seconds');

                game_over(level, time_taken, llamas_counter.html());
            }
            // The cell contains a llama -> decrease the number of llamas left to find
            else if (content === "L") {
                btn.val(content);

                var llamas_left = llamas_counter.html();
                llamas_left--;
                llamas_counter.html(llamas_left);

                // All llamas were found -> game over -> stop the timer -> get the current time
                if (llamas_left == 0) {
                    clock.timer('pause');
                time_taken = clock.data('seconds');
                    game_over(level, time_taken, llamas_left);
                }
            }
            else {
                btn.val(content);
            }
        });
    }
}

// Event when the user right clicks on a the grid
function on_right_click(btn, mines_left) {

    // Check that the cell's content has not been revealed yet,
    // or that the cell has been flagged
    if(btn.val() === "" || btn.val() === "F") {
        var flagged = btn.val() === "F";

        // Unflag the cell and increment the number of mines left to find
        if (flagged) {
            btn.val("");
            mines_left++;
        }
        // Flag the cell and decrement the number of mines left to find
        else {
            btn.val("F");
            mines_left--;
        }
    }
    return mines_left;
}

// Reveal the rest of the grid,
// display the game score and a fraction of the leaderboard
function game_over(level, time_taken, llamas_left) {
    // Call 'end_game' view
    $.get('/llamalandmine/end_game/', {}, function (response) {

        // Convert list of cells to reveal into JSON
        var remaining = JSON.parse(response);

        // Display content of all the remaining cells
        $.each(remaining, function(index, value) {
            if(value[2] === "M") {
                $(".grid_btn[data-row="+value[0]+"][data-column="+value[1]+"]").val("M");
            }
            else if(value[2] === "L") {
                $(".grid_btn[data-row="+value[0]+"][data-column="+value[1]+"]").val(value[2]);
            }
            else {
                $(".grid_btn[data-row="+value[0]+"][data-column="+value[1]+"]").val(value[2]);
            }
        });
    });

    // Call 'game_over' view
    var view = '/llamalandmine/game_over/';
    var data = {level: level, time_taken: time_taken, llamas_left: llamas_left};
    var action = function(stats) {
        // Add the content of the game_over template to the 'game_over' div
        $("#game_over").html(stats);
        window.location.href = "#game_over";
    };

    post_request_handler(view, data, action);
}