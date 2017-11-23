django.jQuery(function ($) {
    'use strict';
    var $type_field = $('#id_type'),
        $floorplan_set = $('#floorplan_set-group'),
        $floorplans_length = $floorplan_set.find('.inline-related.has_original').length,
        type_change_event = function (e) {
            var value = $type_field.val();
            if (value === 'indoor') {
                $floorplan_set.show();
            } else if (value === 'outdoor' && $floorplans_length === 0) {
                $floorplan_set.hide();
            } else if (value === 'outdoor' && $floorplans_length > 0) {
                var msg = 'Please remove the associated floorplans first ' +
                          'and save; then you can switch to type "indoor"';
                alert(gettext(msg));
                e.preventDefault();
                $type_field.val('indoor');
            }
        };
    $type_field.change(type_change_event);
    type_change_event();
});
