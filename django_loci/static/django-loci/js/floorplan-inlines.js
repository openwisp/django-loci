django.jQuery(function ($) {
  "use strict";
  var $type_field = $("#id_type"),
    $floorplan_set = $("#floorplan_set-group"),
    $floorplans_length = $floorplan_set.find(
      ".inline-related.has_original",
    ).length,
    type_change_event = function (e) {
      var value = $type_field.val();
      if (value === "indoor") {
        $floorplan_set.show();
      } else if (value === "outdoor" && $floorplans_length >= 0) {
        $floorplan_set.hide();
      }
    };
  $type_field.change(type_change_event);
  type_change_event();
});
