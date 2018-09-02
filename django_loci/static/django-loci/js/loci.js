/*
this JS is shared between:
    - DeviceLocationForm
    - LocationForm
*/
django.jQuery(function ($) {
    'use strict';

    var $outdoor = $('.loci.coords'),
        $indoor = $('.indoor.coords'),
        $allSections = $('.coords'),
        $geoRows = $('.loci.coords .form-row'),
        $geoEdit = $('.field-name, .field-type, .field-is_mobile, ' +
                     '.field-address, .field-geometry', '.loci.coords'),
        $indoorRows = $('.indoor.coords .form-row:not(.field-indoor)'),
        $indoorEdit = $('.indoor.coords .form-row:not(.field-floorplan_selection)'),
        $indoorPositionRow = $('.indoor.coords .field-indoor'),
        geometryId = $('.field-geometry label').attr('for'),
        mapName = 'leafletmap' + geometryId + '-map',
        loadMapName = 'loadmap' + geometryId + '-map',
        $typeRow = $('.inline-group .field-type'),
        $type = $typeRow.find('select'),
        $isMobile = $('.coords .field-is_mobile input'),
        $locationSelectionRow = $('.field-location_selection'),
        $locationSelection = $locationSelectionRow.find('select'),
        $locationRow = $('.loci.coords .field-location'),
        $location = $locationRow.find('select, input'),
        $locationLabel = $('.field-location .item-label'),
        $name = $('.field-name input', '.loci.coords'),
        $address = $('.field-address input', '.loci.coords'),
        $geometryTextarea = $('.field-geometry textarea'),
        baseLocationJsonUrl = $('#loci-location-json-url').attr('data-url'),
        baseLocationFloorplansJsonUrl = $('#loci-location-floorplans-json-url').attr('data-url'),
        $geometryRow = $geometryTextarea.parents('.form-row'),
        msg = gettext('Location data not received yet'),
        $noLocationDiv = $('.no-location', '.loci.coords'),
        $floorplanSelectionRow = $('.indoor.coords .field-floorplan_selection'),
        $floorplanSelection = $floorplanSelectionRow.find('select'),
        $floorplanRow = $('.indoor .field-floorplan'),
        $floorplan = $floorplanRow.find('select').eq(0),
        $floorplanImage = $('.indoor.coords .field-image input'),
        $floorplanMap = $('.indoor.coords .floorplan-widget');

    // define dummy gettext if django i18n is not enabled
    if (!gettext) { window.gettext = function (text) { return text; }; }

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
            $type.val('');
        }
        $location.val('');
        $locationLabel.text('');
        $isMobile.prop('checked', false);
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
        // reset values
        $indoorEdit.find('input,select').val('');
    }

    function resetDeviceLocationForm() {
        resetOutdoorForm();
        resetIndoorForm();
    }

    function indoorForm(selection) {
        if ($type.val() !== 'indoor') { return; }
        $indoorPositionRow.hide();
        $indoor.show();
        if (!selection) {
            $indoorRows.hide();
            $floorplanSelectionRow.show();
        } else if (selection === 'new') {
            $indoorRows.show();
            $floorplan.val('');
            $floorplanRow.hide();
        }
        if ($locationSelection.val() === 'new') {
            $floorplanSelection.val('new');
            $floorplanSelectionRow.hide();
        }
    }

    function locationSelectionChange(e, initial) {
        var value = $locationSelection.val();
        $allSections.hide();
        if (!initial) { resetDeviceLocationForm(); }
        if (value === 'new') {
            $outdoor.show();
            $geoRows.hide();
            $typeRow.show();
            indoorForm(value);
        } else if (value === 'existing') {
            $outdoor.show();
            $geoRows.hide();
            $locationRow.show();
        }
    }

    function typeChange(e, initial) {
        var value = $type.val();
        if (value) {
            $outdoor.show();
            $geoEdit.show();
            invalidateMapSize();
        } else {
            $geoEdit.hide();
            $indoor.hide();
            $typeRow.show();
        }
        if (value === 'indoor') {
            $indoor.show();
            $indoorRows.show();
            indoorForm($locationSelection.val());
        } else {
            $indoor.hide();
        }
    }

    function floorplanSelectionChange(e, initial) {
        var value = $floorplanSelection.val(),
            optionsLength = $floorplan.find('option').length;
        // do not reset indoor form at first load
        if (!initial) {
            resetIndoorForm(true);
        }
        indoorForm(value);
        if (value === 'existing' && optionsLength > 1) {
            $floorplanRow.show();
        // if no floorplan available, make it obvious
        } else if (value === 'existing' && optionsLength <= 1) {
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

    function locationChange(e, initial) {
        function loadIndoor() {
            indoorForm();
            if ($type.val() !== 'indoor') { return; }
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
        $typeRow.show();
        if (!initial) {
            // update location fields
            var url = getLocationJsonUrl($location.val());
            $.getJSON(url, function (data) {
                $locationLabel.text(data.name);
                $name.val(data.name);
                $type.val(data.type);
                $isMobile.prop('checked', data.is_mobile);
                $address.val(data.address);
                $geometryTextarea.val(JSON.stringify(data.geometry));
                var map = getMap();
                if (map) { map.remove(); }
                $geoEdit.show();
                window[loadMapName]();
                loadIndoor();
            });
        } else {
            loadIndoor();
        }
    }

    $location.change(locationChange);
    locationChange(null, true);

    $isMobile.change(function () {
        var rows = [
            $name.parents('.form-row'),
            $address.parents('.form-row'),
            $geometryRow
        ];
        if ($isMobile.prop('checked')) {
            $(rows).each(function (i, el) {
                $(el).hide();
            });
        } else {
            $(rows).each(function (i, el) {
                $(el).show();
            });
        }
    });

    $floorplanSelection.change(floorplanSelectionChange);
    floorplanSelectionChange(null, true);

    $floorplan.change(function () {
        // reset floorplan data if no floorplan is chosen
        if (!$floorplan.val()) {
            resetIndoorForm(true);
            $indoorRows.show();
            $indoorEdit.hide();
            $floorplanRow.show();
            return;
        }
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

    $('#content-main form').submit(function (e) {
        var indoorPosition = $('.field-indoor .floorplan-raw input').val();
        if ($type.val() === 'indoor' && !indoorPosition) {
            e.preventDefault();
            alert(gettext('Please set the indoor position before saving'));
        }
    });

    // websocket for mobile coords
    function listenForLocationUpdates(pk) {
        var host = window.location.host,
            protocol = window.location.protocol === 'http:' ? 'ws' : 'wss',
            ws = new WebSocket(protocol + '://' + host + '/ws/loci/location/' + pk + '/');
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
    if ($isMobile.prop('checked')) {
        listenForLocationUpdates($location.val());
        $outdoor.show();
        $locationSelection.parents('.form-row').hide();
        $locationRow.hide();
        $name.parents('.form-row').hide();
        $address.parents('.form-row').hide();
        // if no location data yet
        if (!$geometryTextarea.val()) {
            $geometryRow.hide();
            $geometryRow.parent().append('<div class="no-location">' + msg + '</div>');
            $noLocationDiv = $('.no-location', '.loci.coords');
        }
    // this is triggered in the location form page
    } else if (!$type.length) {
        var pk = window.location.pathname.split('/').slice('-3', '-2')[0];
        if (pk !== 'location') { listenForLocationUpdates(pk); }
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
