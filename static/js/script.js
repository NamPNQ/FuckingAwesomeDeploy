/**
 * Created by nampnq on 22/03/2015.
 */

$(function(){
    $(document).on('click', '.edit-stage-btn', function(){
        var $this = $(this);
        $this.closest('li').find('.panel-edit-stage').toggle();
    });
});