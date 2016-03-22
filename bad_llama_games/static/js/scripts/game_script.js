$(document).ready(function() {

	// Div element containing the game grid
    var grid_div = $('#grid');

	// Do not display context menu when the user right clicks on a cell
    grid_div.attr('oncontextmenu','return false;');

    var grid_size = grid_div.attr('data-size');

	// Timer
    var clock = $('.clock').FlipClock({
        clockFace: 'MinuteCounter',
        autoStart: false
    });

    var first_click = false;

	// Add buttons to grid div
    for(var i = 0; i < grid_size; i++) {

        var cells_row = $("<div class='row'>");

        for(var j = 0; j < grid_size; j++) {
            cells_row.append($("<button/>", {
                id: 'btn_' + i + '_' + j,
                row: i,
                column: j,
                text: "",


				// Event when the user clicks on the grid
                mousedown: function (event) {

					// Start the timer when the user clicks for the first time
                    if(!first_click) {
                        first_click = true;
                        clock.start();
                    }

					// Get the coordinates of the cell the user clicked on
                    var row = $(this).attr('row');
                    var column = $(this).attr('column');

                    switch (event.which) {
                        case 1:
                            on_left_click(row, column, clock, grid_div);
                            break;

                        case 3:
                            // Update number of mines left
                            // when the user flags or unflags a cell
                            var mines_counter = $('#mines_counter');
                            var mines_left = mines_counter.html();
                            mines_left = on_right_click(row, column, mines_left);
                            mines_counter.html(mines_left);
                            break;

                        default:
                            break;
                    }
                }
            }).addClass("btn-game"));
        }

        grid_div.append(cells_row);
    }
});

// Event when the user left clicks on a the grid
function on_left_click(row, column, clock, grid_div) {

    if($('#btn_' + row + '_' + column).text() === "") {
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
                    $('#btn_' + value[0] + '_' + value[1]).text(value[2]);
                });
            }
            // The cell contains a mine -> game over -> stop the timer -> get the current time
            else if (content === "M") {
                $('#btn_' + row + '_' + column).text("X");

                clock.stop(function () {
                    time_taken = clock.getTime().getTimeSeconds();
                });
                game_over(level, time_taken, llamas_counter.html());
            }
            // The cell contains a llama -> decrease the number of llamas left to find
            else if (content === "L") {
                $('#btn_' + row + '_' + column).text(content);

                var llamas_left = llamas_counter.html();
                llamas_left--;
                llamas_counter.html(llamas_left);

                // All llamas were found -> game over -> stop the timer -> get the current time
                if (llamas_left == 0) {
                    clock.stop(function () {
                        time_taken = clock.getTime().getTimeSeconds();
                    });
                    game_over(level, time_taken, llamas_left);
                }
            }
            else {
                $('#btn_' + row + '_' + column).text(content);
            }
        });
    }
        }
        else {
            $('#btn_'+row+'_'+column).val(content);
        }
    });
}

// Event when the user right clicks on a the grid
function on_right_click(row, column, mines_left) {
    var cell = $('#btn_'+row+'_'+column);

    // Check that the cell's content has not been revealed yet,
    // or that the cell has been flagged
    if(cell.text() === "" || cell.text() === "F") {
        var flagged = cell.text() === "F";

        // Unflag the cell and increment the number of mines left to find
        if (flagged) {
            cell.text("");
            mines_left++;
        }
        // Flag the cell and decrement the number of mines left to find
        else {
            cell.text("F");
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
                $('#btn_' + value[0] + '_' + value[1]).text("X");
            }
            else if(value[2] === "L") {
                $('#btn_' + value[0] + '_' + value[1]).text(value[2]);
            }
            else {
                $('#btn_' + value[0] + '_' + value[1]).text(value[2]);
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