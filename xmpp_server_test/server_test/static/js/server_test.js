var refresh_test = function() {
    console.log('Refreshing test...');
    $.get(refresh_url, function(data) {
        $('#servertest-details.in-progress').replaceWith(data);
    });

    window.setTimeout(refresh_content, 3000);
}

$(document).ready(function() {
    window.setTimeout(refresh_content, 3000);
});
