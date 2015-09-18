var refresh_test = function() {
    var details = $('#servertest-details');
    if (details.hasClass('in-progress')) {
        $.get(refresh_url, function(data) {
            details.replaceWith(data);
        });
        if ($('#servertest-details').hasClass('in-progress')) {
            window.setTimeout(refresh_test, 3000);
        }
    }
}

$(document).ready(function() {
    window.setTimeout(refresh_test, 3000);
});
