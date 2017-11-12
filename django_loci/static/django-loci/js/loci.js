/*
this JS is shared between:
    - DeviceLocationForm
    - LocationForm
*/
django.jQuery(function ($) {
    'use strict';

    var $outdoor = $('.geo.coords'),
        $indoor = $('.indoor.coords'),
        $allSections = $('.coords'),
        $geoRows = $('.geo.coords .form-row:not(.field-location_selection)'),
        $geoEdit = $('.field-name, .field-address, .field-geometry', '.geo.coords'),
        $indoorRows = $('.indoor.coords .form-row:not(.field-indoor)'),
        geometryId = $('.field-geometry label').attr('for'),
        mapName = 'leafletmap' + geometryId + '-map',
        loadMapName = 'loadmap' + geometryId + '-map',
        $type = $('.inline-group .field-type select'),
        $locationSelectionRow = $('.geo.coords .field-location_selection'),
        $locationSelection = $locationSelectionRow.find('select'),
        $locationRow = $('.geo.coords .field-location'),
        $location = $locationRow.find('select, input'),
        $locationLabel = $('.field-location .item-label'),
        $name = $('.field-name input', '.geo.coords'),
        $address = $('.field-address input', '.geo.coords'),
        $geometryTextarea = $('.field-geometry textarea'),
        baseLocationJsonUrl = $('#geo-location-json-url').attr('data-url'),
        baseLocationFloorplansJsonUrl = $('#geo-location-floorplans-json-url').attr('data-url'),
        $geometryRow = $geometryTextarea.parents('.form-row'),
        msg = gettext('Location data not received yet'),
        $noLocationDiv = $('.no-location', '.geo.coords'),
        $floorplanSelectionRow = $('.indoor.coords .field-floorplan_selection'),
        $floorplanSelection = $floorplanSelectionRow.find('select'),
        $floorplanRow = $('.indoor .field-floorplan'),
        $floorplan = $floorplanRow.find('select').eq(0),
        $floorplanImage = $('.indoor.coords .field-image input'),
        $floorplanMap = $('.indoor.coords .floorplan-widget');

    function getLocationJsonUrl(pk) {
        return baseLocationJsonUrl.replace('0000', pk);
    }

    function getLocationFloorplansJsonUrl(pk) {
        return baseLocationFloorplansJsonUrl.replace('0000', pk);
    }

    function getMap() {
        return window[mapName];
    }

    function invalidateMapSize() {
        var map = getMap();
        if (map) { map.invalidateSize(); }
        return map;
    }

    function resetOutdoorForm(keepLocationSelection) {
        $locationSelectionRow.show();
        if (!keepLocationSelection) {
            $locationSelection.val('');
        }
        $location.val('');
        $locationLabel.text('');
        $name.val('');
        $address.val('');
        $geometryTextarea.val('');
        $geoEdit.hide();
        $locationRow.hide();
        $locationSelection.show();
        $noLocationDiv.hide();
    }

    function resetIndoorForm(keepFloorplanSelection) {
        if (!keepFloorplanSelection) {
            $indoor.hide();
            $floorplanSelection.val('');
        }
        $indoorRows.hide();
        $floorplanSelectionRow.show();
        $floorplan.val('');
    }

    function resetDeviceLocationForm() {
        resetOutdoorForm();
        resetIndoorForm();
    }

    function indoorForm(selection) {
        if ($type.val() !== 'indoor') { return; }
        $indoor.show();
        if (selection === 'new') {
            $indoorRows.show();
            $floorplan.val('');
            $floorplanRow.hide();
        }
        if ($locationSelection.val() === 'new') {
            $floorplanSelection.val('new');
            $floorplanSelectionRow.hide();
        }
    }

    function typeChange(e, initial) {
        var value = $type.val();
        $allSections.hide();
        if (!initial) { resetDeviceLocationForm(); }
        if (value === 'outdoor' || value === 'indoor') {
            $outdoor.show();
        }
    }

    function locationSelectionChange(e, initial) {
        var value = $locationSelection.val();
        $geoRows.hide();
        if (!initial) {
            resetOutdoorForm(true);
            resetIndoorForm();
        }
        if (value === 'new') {
            $geoEdit.show();
            indoorForm(value);
        } else if (value === 'existing') {
            $locationRow.show();
        }
        invalidateMapSize();
    }

    function floorplanSelectionChange() {
        var value = $floorplanSelection.val(),
            optionsLength = $floorplan.find('option').length;
        if (value === 'new') {
            indoorForm(value);
        }
        if (value === 'existing' && optionsLength > 1) {
            $floorplanRow.show();
        }
        // if no floorplan available, make it obvious
        else if (value === 'existing' && optionsLength <= 1) {
            alert(gettext('This location has no floorplans available yet'));
            $floorplanSelection.val('');
        }
    }

    // HACK to override `dismissRelatedLookupPopup()` and
    // `dismissAddAnotherPopup()` in Django's RelatedObjectLookups.js to
    // trigger change event when an ID is selected or added via popup.
    function triggerChangeOnField(win, chosenId) {
        $(document.getElementById(windowname_to_id(win.name))).change();
    }
    window.ORIGINAL_dismissRelatedLookupPopup = window.dismissRelatedLookupPopup;
    window.dismissRelatedLookupPopup = function (win, chosenId) {
        window.ORIGINAL_dismissRelatedLookupPopup(win, chosenId);
        triggerChangeOnField(win, chosenId);
    };
    window.ORIGINAL_dismissAddAnotherPopup = window.dismissAddAnotherPopup;
    window.dismissAddAnotherPopup = function (win, chosenId) {
        window.ORIGINAL_dismissAddAnotherPopup(win, chosenId);
        triggerChangeOnField(win, chosenId);
    };

    $type.change(typeChange);
    typeChange(null, true);

    $locationSelection.change(locationSelectionChange);
    locationSelectionChange(null, true);

    function locationChange() {
        var url = getLocationJsonUrl($location.val());
        $.getJSON(url, function (data) {
            $locationLabel.text(data.name);
            $name.val(data.name);
            $address.val(data.address);
            $geometryTextarea.val(JSON.stringify(data.geometry));
            var map = getMap();
            if (map) { map.remove(); }
            $geoEdit.show();
            window[loadMapName]();
        });
        indoorForm();
        if ($type.val() === 'indoor') {
            var floorplansUrl = getLocationFloorplansJsonUrl($location.val());
            $.getJSON(floorplansUrl, function (data) {
                var $current = $floorplan.find('option:selected'),
                    currentValue = $current.val();
                $floorplan.find('option[value!=""]').remove();
                $(data.choices).each(function (i, el) {
                    var o = $('<option></option>').attr('value', el.id)
                                                  .text(el.str)
                                                  .data('floor', el.floor)
                                                  .data('image', el.image)
                                                  .data('image_width', el.image_width)
                                                  .data('image_height', el.image_height);
                    if (el.id === currentValue) {
                        o.attr('selected', 'selected');
                    }
                    $floorplan.append(o);
                });
            });
        }
    }

    $location.change(locationChange);
    locationChange();

    $floorplanSelection.change(floorplanSelectionChange);
    floorplanSelectionChange();

    $floorplan.change(function () {
        if (!$floorplan.val()) { return; }
        var option = $floorplan.find('option:selected'),
            widgetName = $floorplanMap.parents('.field-indoor')
                                      .find('.floorplan-widget')
                                      .attr('id')
                                      .replace('id_', '')
                                      .replace('_map', ''),
            globalName = 'django-loci-floorplan-' + widgetName,
            image = option.data('image'),
            $a = $indoor.find('.field-image a'),
            $aText = $a.text(),
            $aNewText = $aText.split(': ')[0] + ': ' + image.split('/').slice(-1);
        $indoor.find('.field-floor input').val(option.data('floor'));
        $indoor.find('.form-row:not(.field-floorplan_selection)').show();
        $a.attr('href', image).text($aNewText);
        // remove previous indoor map if present
        if (window[globalName]) {
            window[globalName].remove();
        }
        window[globalName] = django.loadFloorPlan(
            widgetName,
            image,
            option.data('image_width'),
            option.data('image_height')
        );
    });

    $floorplanImage.change(function () {
        var input = this,
            reader = new FileReader(),
            image = new Image(),
            $indoorRow = $floorplanMap.parents('.field-indoor'),
            widgetName = $indoorRow.find('.floorplan-widget')
                                   .attr('id')
                                   .replace('id_', '')
                                   .replace('_map', ''),
            globalName = 'django-loci-floorplan-' + widgetName;
        if (!input.files || !input.files[0]) {
            return;
        }
        reader.onload = function (e) {
            image.src = e.target.result;
            image.onload = function () {
                $indoorRow.show();
                // remove previous indoor map if present
                if (window[globalName]) {
                    window[globalName].remove();
                }
                window[globalName] = django.loadFloorPlan(
                    widgetName,
                    this.src,
                    this.width,
                    this.height
                );
            };
        };
        reader.readAsDataURL(input.files[0]);
    });

    // websocket for mobile coords
    function listenForLocationUpdates(pk) {
        var ws = new WebSocket('ws://' + window.location.host + '/geo/mobile-location/' + pk + '/');
        ws.onmessage = function (e) {
            $geometryRow.show();
            $noLocationDiv.hide();
            $geometryTextarea.val(e.data);
            getMap().remove();
            window[loadMapName]();
        };
    }

    // show existing location
    if ($location.val()) {
        $locationSelectionRow.hide();
        $geoEdit.show();
    }
    // show mobile map (hide not relevant fields)
    if ($type.val() === 'mobile') {
        $outdoor.show();
        $locationSelection.parents('.form-row').hide();
        $locationRow.hide();
        $name.parents('.form-row').hide();
        $address.parents('.form-row').hide();
        // if no location data yet
        if (!$geometryTextarea.val()) {
            $geometryRow.hide();
            $geometryRow.parent().append('<div class="no-location">' + msg + '</div>');
            $noLocationDiv = $('.no-location', '.geo.coords');
        }
        listenForLocationUpdates($location.val());
    } else if (!$type.length) {
        var pk = window.location.pathname.split('/').slice('-3', '-2')[0];
        listenForLocationUpdates(pk);
    }
    // show existing indoor
    if ($floorplan.val()) {
        $indoor.show();
        $indoorRows.show();
        $floorplanSelectionRow.hide();
    // adding indoor
    } else if ($type.val() === 'indoor') {
        $indoor.show();
        $indoorRows.show();
    }
});
