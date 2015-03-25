/**
 * Created by nampnq on 22/03/2015.
 */

$(function () {
    $(document).on('click', '.edit-stage-btn', function () {
        var $this = $(this);
        $this.closest('li').find('.panel-edit-stage').toggle();
    });
});

function startStream() {
    $(document).ready(function () {
        var following = true;
        var $messages = $("#messages");
        var streamUrl = $("#output").data("streamUrl");
        var source = new EventSource(streamUrl);

        var addLine = function (data) {
            var msg = JSON.parse(data).msg;
            $messages.append(msg);
            if (following) {
                $messages.scrollTop($messages[0].scrollHeight);
            }
        };

        var updateStatus = function (e) {
            var data = JSON.parse(e.data);
            $('#header').html(data.html);
        };

        source.addEventListener('append', function (e) {
            $messages.trigger('contentchanged');
            addLine(e.data);
        }, false);

        source.addEventListener('started', function (e) {
            updateStatus(e);
        }, false);

        source.addEventListener('finished', function (e) {
            updateStatus(e);
            toggleOutputToolbar();
            timeAgoFormat();
            source.close();
        }, false);
    });
};
function toggleOutputToolbar() {
    $('.only-active, .only-finished').toggle();
}