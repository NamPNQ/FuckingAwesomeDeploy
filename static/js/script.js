/**
 * Created by nampnq on 22/03/2015.
 */

$.fn.serializeObject = function(){
         var o = {};
         var a = this.serializeArray();
         $.each(a, function() {
             if (o[this.name]) {
                 if (!o[this.name].push) {
                     o[this.name] = [o[this.name]];
                 }
                 o[this.name].push(this.value || '');
             } else {
                 o[this.name] = this.value || '';
             }
         });
         return o;
      };

$(function () {
    $(document).on('click', '.edit-stage-btn', function () {
        var $this = $(this);
        $this.closest('li').find('.panel-edit-stage').toggle();
    });
    $('.new-stage-btn').click(function(){
        $('.new-stage-item').show();
    });
    $('.new-stage-form').submit(function(e){
        e.preventDefault();
        var $this = $(this), url = $this.attr('action-url');
        $.ajax(url, {
            'method': 'POST',
            'dataType': 'json',
            'contentType': 'application/json',
            'data': JSON.stringify($this.serializeObject())
        }).success(function(data){
            if(data.status=='ok'){
                var $new_stage_item = $('.new-stage-item'), $clone_item = $new_stage_item.clone();
                $new_stage_item.hide();
                var $tmp_arr = $clone_item.find('form').attr('action-url').split('/');
                $tmp_arr[$tmp_arr.length-1] = 'update';
                $tmp_arr.push($this.serializeObject()['name']);
                var $clone_url_update = $tmp_arr.join('/');
                $clone_item.removeClass('new-stage-item');
                $('form', $clone_item)
                    .removeClass('new-stage-form')
                    .addClass('edit-stage-form')
                    .attr('action-url', $clone_url_update);
                $('.edit-stage-btn', $clone_item).html($this.serializeObject()['name']);
                $('.panel-edit-stage', $clone_item).hide();
                $clone_item.insertBefore($('#stages').find('.new-stage-item'));
                $new_stage_item.find('form')[0].reset();
            }
        }).error()
    });
    $(document).on('submit', '.edit-stage-form', function(e){
        e.preventDefault();
        var $this = $(this), url = $this.attr('action-url');
        $.ajax(url, {
            'method': 'POST',
            'dataType': 'json',
            'contentType': 'application/json',
            'data': JSON.stringify($this.serializeObject())
        }).success(function(){
            $this.closest('.panel-edit-stage').hide();
        });
    });
    $(document).on('click', '.cancel-save-stage', function(){
        var $this = $(this);
        $this.closest('.new-stage-item').hide();
    })
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
}
function toggleOutputToolbar() {
    $('.only-active, .only-finished').toggle();
}