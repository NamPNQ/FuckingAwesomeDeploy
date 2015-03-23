/**
 * Created by nampnq on 22/03/2015.
 */

$(function(){
    $('.edit-stage-btn').click(function(){
        $this = $(this);
        $this.closest('li').find('.panel-edit-stage').toggle();
    })
})