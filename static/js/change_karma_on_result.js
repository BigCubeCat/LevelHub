function plus_karma_result(level_id) {
    $.ajax({
        type: "POST",
        url: "/button_like_result/" + level_id,
        data: "",
        error: function (error) {
            console.log(error);
        }
    });
}

function minus_karma_result(level_id) {
    $.ajax({
        type: "POST",
        url: "/button_dislike_result/" + level_id,
        data: "",
        error: function (error) {
            console.log(error);
        }
    });
}
