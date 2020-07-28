function plus_karma(level_id) {
    $.ajax({
        type: "POST",
        url: "/button_like/" + level_id,
        data: "",
        error: function (error) {
            console.log(error);
        }
    });
}

function minus_karma(level_id) {
    $.ajax({
        type: "POST",
        url: "/button_dislike/" + level_id,
        data: "",
        error: function (error) {
            console.log(error);
        }
    });
}
