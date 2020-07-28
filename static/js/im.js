$(document).ready(function () {
    let reader = new FileReader();
    let imageInput = $('#photo'); // <input type=file>
    let image = $('#im'); // <img>
    imageInput.change(function (event) {
        let file = event.target.files[0];
        reader.readAsDataURL(file);
        reader.onload = function () {
            image.attr('src', reader.result);
        }
    });
});