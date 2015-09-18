var refresh_test = function() {
    var details = $('#servertest-details');
    if (details.hasClass('in-progress')) {
        $('#servertest-details').load(refresh_url, function() {
            if ($('#servertest-details').hasClass('in-progress')) {
                window.setTimeout(refresh_test, 3000);
            }
        });
    }
}

$(document).ready(function() {
    window.setTimeout(refresh_test, 3000);
});
