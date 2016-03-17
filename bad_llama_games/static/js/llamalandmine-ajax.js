
$(document).ready(function() {
    console.log("in ajax");
    var grid_div = $('#grid');
    grid_div.attr('oncontextmenu','return false;');
    var grid_size = grid_div.attr('data-size');

    var clock = $('.clock').FlipClock({
        clockFace: 'MinuteCounter',
        autoStart: false
    });

    var first_click = false;

    for(var i = 0; i < grid_size; i++) {
        var cells_row = $("<div class='row'>");

        for(var j = 0; j < grid_size; j++) {
            cells_row.append($("<button/>", {
                id: 'btn_' + i + '_' + j,
                row: i,
                column: j,
                text: "",
                mousedown: function (event) {
                    if(!first_click) {
                        first_click = true;
                        clock.start();
                    }
                    var row = $(this).attr('row');
                    var column = $(this).attr('column');

                    switch (event.which) {
                        case 1:
                            on_left_click(row, column, clock);
                            break;

                        case 3:
                            var mines_counter = $('#mines_counter');
                            var mines_left = mines_counter.html();
                            if(on_right_click(row, column)){
                                mines_left--;
                            }
                            else {
                                mines_left++;
                            }
                            mines_counter.html(mines_left);
                            break;

                        default:
                            break;
                    }
                }
            }).height(20));
        }
        grid_div.append(cells_row);
    }

});

function on_left_click(row, column, clock) {
    $.get('/llamalandmine/get_grid_data/', {row: row, column: column}, function (response) {
        var content = JSON.parse(response);

        if($.isArray(content)) {
            $.each(content, function (index, value) {
                $('#btn_' + value[0] + '_' + value[1]).text(value[2]);
            });
        }
        else if(content === "M") {
            $('#btn_'+row+'_'+column).text("X");
            clock.stop();
            // CALL VIEW GAME OVER + DISPLAY ALL GRID
        }
        else if(content === "L") {
            $('#btn_'+row+'_'+column).text("L");

            var llamas_counter = $('#llamas_counter');
            var llamas_left = llamas_counter.html();
            llamas_left--;
            llamas_counter.html(llamas_left);

            if(llamas_left == 0){
                // CALL VIEW GG WIN
            }
        }
        else {
            $('#btn_'+row+'_'+column).text(content);
        }
    });
}

function on_right_click(row, column) {
    var cell = $('#btn_'+row+'_'+column);
    var flagged = cell.text() === "F";

    if(flagged) {
        cell.text("");
        return false;
    }
    else{
        cell.text("F");
        return true;
    }
}

