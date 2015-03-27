/**
 * Created by nampnq on 22/03/2015.
 */
var following = true;

(function (original) {
  jQuery.fn.clone = function () {
    var result           = original.apply(this, arguments),
        my_textareas     = this.find('textarea').add(this.filter('textarea')),
        result_textareas = result.find('textarea').add(result.filter('textarea')),
        my_selects       = this.find('select').add(this.filter('select')),
        result_selects   = result.find('select').add(result.filter('select'));

    for (var i = 0, l = my_textareas.length; i < l; ++i) $(result_textareas[i]).val($(my_textareas[i]).val());
    for (var i = 0, l = my_selects.length;   i < l; ++i) {
      for (var j = 0, m = my_selects[i].options.length; j < m; ++j) {
        if (my_selects[i].options[j].selected === true) {
          result_selects[i].options[j].selected = true;
        }
      }
    }
    return result;
  };
}) (jQuery.fn.clone);

$.fn.serializeObject = function () {
    var o = {};
    var a = this.serializeArray();
    $.each(a, function () {
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
    $('.new-stage-btn').click(function () {
        $('.new-stage-item').show();
    });
    $('.new-stage-form').submit(function (e) {
        e.preventDefault();
        var $this = $(this), url = $this.attr('action-url');
        $.ajax(url, {
            'method': 'POST',
            'dataType': 'json',
            'contentType': 'application/json',
            'data': JSON.stringify($this.serializeObject())
        }).success(function (data) {
            if (data.status == 'ok') {
                var $new_stage_item = $('.new-stage-item'), $clone_item = $new_stage_item.clone();
                $new_stage_item.hide();
                var $tmp_arr = $clone_item.find('form').attr('action-url').split('/');
                $tmp_arr[$tmp_arr.length - 1] = 'update';
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
            else {
                alert('Update failed');
            }
        }).error()
    });
    $(document).on('submit', '.edit-stage-form', function (e) {
        e.preventDefault();
        var $this = $(this), url = $this.attr('action-url');
        $.ajax(url, {
            'method': 'POST',
            'dataType': 'json',
            'contentType': 'application/json',
            'data': JSON.stringify($this.serializeObject())
        }).success(function () {
            $this.closest('.panel-edit-stage').hide();
        });
    });
    $(document).on('click', '.cancel-save-stage', function () {
        var $this = $(this);
        $this.closest('.new-stage-item').hide();
    });
    $('.users.index .role').find('input[type=radio]').change(function () {
        var $this = $(this), user_id = $this.closest('.role').data('user-id');
        $.ajax('/admin/users/' + user_id, {
            'method': 'POST',
            'dataType': 'json',
            'contentType': 'application/json',
            'data': JSON.stringify({'role': $this.val()})
        })
    });
    $("#output-follow").click(function (event) {
        following = true;

        shrinkOutput();

        var $messages = $("#messages");
        $messages.scrollTop($messages.prop("scrollHeight"));

        $("#output-options > button, #output-grow-toggle").removeClass("active");
        $(this).addClass("active");
    });
    $("#output-steady").click(function (event) {
        following = false;

        shrinkOutput();

        $("#output-options > button").removeClass("active");
        $(this).addClass("active");
    });
    $("#output-grow").click(function (event) {
        growOutput();

        $("#output-options > button").removeClass("active");
        $(this).addClass("active");
        $("#output-grow-toggle").addClass("active");
    });
    $("#output-grow-toggle").click(function (event) {
        var $self = $(this);

        if ($self.hasClass("active")) {
            shrinkOutput();
            $self.removeClass("active");
        } else {
            growOutput();
            $self.addClass("active");
        }
    });

});

function startStream() {
    $(document).ready(function () {
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
            source.close();
            setTimeout(function(){window.location.reload();},500)
        }, false);
    });
}
function toggleOutputToolbar() {
    $('.only-active, .only-finished').toggle();
}
function shrinkOutput() {
    $("#messages").css("max-height", 550);
}

function growOutput() {
    $("#messages").css("max-height", "none");
}