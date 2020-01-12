/*global
alert, confirm, console, Debug, opera, prompt, WSH
*/
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
        $isMobile = $('.coords .field-is_mobile input, #location_form .field-is_mobile input'),
        $locationSelectionRow = $('.field-location_selection'),
        $locationSelection = $locationSelectionRow.find('select'),
        $locationRow = $('.loci.coords .field-location'),
        $location = $locationRow.find('select, input'),
        $locationLabel = $('.field-location .item-label'),
        $name = $('.field-name input', '.loci.coords'),
        $address = $('.coords .field-address input, #location_form .field-address input'),
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
        $floorplanMap = $('.indoor.coords .floorplan-widget'),
        isNew = true;
        $addressInput = $('.field-address input'),
        $mapGeojsonTextarea = $('.django-leaflet-raw-textarea'),
        $form = $('form');

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
        if (!$floorplanSelection.val()) {
            $indoorRows.hide();
            $floorplanSelectionRow.show();
        }
    }

    function locationSelectionChange(e, initial) {
        var value = $locationSelection.val();
        $allSections.hide();
        if (!initial) { resetDeviceLocationForm(); }
        if (value === 'new') {
            $outdoor.show();
            $typeRow.show();
            indoorForm(value);
        } else if (value === 'existing') {
            $outdoor.show();
            $locationRow.show();
        }
    }

    function isMobileChange() {
        var rows = [
            $address,
            $geometryTextarea
        ];
        if ($isMobile.prop('checked')) {
            $(rows).each(function (i, el) {
                if (!$(el).val()) {
                    $(el).parents('.form-row').hide();
                }
            });
            // name not relevant in mobile locations
            $name.parents('.form-row').hide();
            if (!$geometryTextarea.val()) { $('.no-location').show(); }
        } else {
            $(rows).each(function (i, el) {
                $(el).parents('.form-row').show();
            });
            $name.parents('.form-row').show();
            $('.no-location').hide();
        }
    }

    function typeChange(e, initial) {
        var value = $type.val();
        if (value) {
            $outdoor.show();
            $geoEdit.show();
            invalidateMapSize();
            isMobileChange();
        } else {
            $geoEdit.hide();
            $indoor.hide();
            $typeRow.show();
        }
        if (value === 'indoor') {
            $indoor.show();
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
            if ($type.val() !== 'indoor') {
                $indoor.hide();
                return;
            }
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
                $geometryTextarea.val(data.geometry ? JSON.stringify(data.geometry) : '');
                var map = getMap();
                if (map) { map.remove(); }
                $geoEdit.show();
                window[loadMapName]();
                isMobileChange();
                loadIndoor();
            });
        } else {
            loadIndoor();
        }
    }

    $location.change(locationChange);
    locationChange(null, true);

    $isMobile.change(isMobileChange);

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
        if (isNew && $type.val() === 'indoor' && !indoorPosition) {
            var message = gettext('You have set this location as indoor but have ' +
                                  'not specified indoor cordinates on a floorplan, ' +
                                  'do you want to save anyway?');
            if (!confirm(message)) {
                e.preventDefault();
            } else {
                $floorplanSelection.val('');
                indoorForm();
            }
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

    // returns placed marker
    function getMarker() {
        var map = getMap();
        if (map !== undefined) {
            var layer;
            for (layer in map._layers) {
                if (map._layers.hasOwnProperty(layer)) {
                    if (map._layers[layer].hasOwnProperty('_latlng') &&
                            map._layers[layer]._events.click === undefined) {
                        return map._layers[layer];
                    }
                }
            }
        } else {
            window.setTimeout(getMarker, 100);
        }
    }

    // returns map's feature group
    function getFeatureGroup() {
        var map = getMap();
        if (map !== undefined) {
            var layer;
            for (layer in map._layers) {
                if (map._layers.hasOwnProperty(layer)) {
                    if (map._layers[layer].hasOwnProperty('_layers')) {
                        return map._layers[layer];
                    }
                }
            }
        } else {
            window.setTimeout(getFeatureGroup, 100);
        }
    }

    // set marker
    function updateMap() {
        if ($addressInput.val() !== '') {
            window.fetch(window.geocodeApi + '?address=' + $addressInput.val())
                    .then(function (resp) {
                    var dataPromise = resp.json();
                    dataPromise.then(function (data) {
                        if (resp.status === 200) {
                            var currentMarkerLat = getMarker() !== undefined ?
                                                        getMarker().getLatLng().lat : null;
                            var currentMarkerLng = getMarker() !== undefined ?
                                                        getMarker().getLatLng().lng : null;

                            if (currentMarkerLat !== data.lat || currentMarkerLng !== data.lng) {
                                var geojson = '{ "type": "Point", "coordinates": [ ' +
                                        data.lng.toString() + ', ' +
                                        data.lat.toString() + '] }';
                                if (getMarker() === undefined) {
                                    getFeatureGroup().addLayer(L.marker([data.lat, data.lng]));
                                    $mapGeojsonTextarea.val(geojson);
                                    window.addressLat = data.lat;
                                    window.addressLng = data.lng;
                                    getMap().setView([data.lat, data.lng], 14);
                                } else {
                                    if (window.skipGeocode === 0) {
                                        if (window.confirm('Do you want to update map?')) {
                                            getFeatureGroup().removeLayer(getMarker());
                                            getFeatureGroup().addLayer(L.marker([data.lat, data.lng]));
                                            $mapGeojsonTextarea.val(geojson);
                                            window.addressLat = data.lat;
                                            window.addressLng = data.lng;
                                            window.skipGeocode = 0;
                                            getMap().setView([data.lat, data.lng], 14);
                                        } else {
                                            window.skipGeocode = 1;
                                        }
                                    } else {
                                        window.skipGeocode -= 1;
                                    }
                                }
                            }
                        } else {
                            if (window.skipGeocode === 0) {
                                alert('Not found location with given name');
                                window.skipGeocode = 1;
                            } else {
                                window.skipGeocode -= 1;
                            }
                        }
                    });
                });
        }
    }

    // wait until dragging is not enabled and update address
    function updateAdress() {
        if (getMarker().dragging._enabled !== true && window.update === true) {
            window.update = false;
            var latLng = getMarker().getLatLng();
            if (window.beforeEditLat !== latLng.lat || window.beforeEditLng !== latLng.lng) {
                var reverseApiWithData = window.reverseApi + '?lat=' + latLng.lat + '&lng=' + latLng.lng;
                window.fetch(reverseApiWithData)
                    .then(function (resp) {
                        var dataPromise = resp.json();
                        dataPromise.then(function (data) {
                            if (resp.status === 200) {
                                $addressInput.val(data.address);
                            } else {
                                var message = 'We couldn\'t find a related address to the location '
                                        + 'selected on the map, please enter the address manually';
                                alert(message);
                                window.skipGeocode = 2;
                            }
                        });
                    });
                window.markerCoords = latLng;
            }
        } else {
            window.setTimeout(updateAdress, 200);
        }
    }

    // show existing location
    var pk;
    if ($location.val()) {
        $locationSelectionRow.hide();
        $geoEdit.show();
        isNew = false;
        pk = $location.val();
    } else {
        pk = window.location.pathname.split('/').slice('-3', '-2')[0];
    }
    // show mobile map (hide not relevant fields)
    if ($isMobile.prop('checked')) {
        listenForLocationUpdates(pk);
        $outdoor.show();
        $locationSelection.parents('.form-row').hide();
        $locationRow.hide();
        $name.parents('.form-row').hide();
        if (!$address.val()) { $address.parents('.form-row').hide(); }
        // if no location data yet
        if (!$geometryTextarea.val()) {
            $geometryRow.hide();
            $geometryRow.parent().append('<div class="no-location">' + msg + '</div>');
            $noLocationDiv = $('.no-location', '.loci.coords');
        }
    // this is triggered in the location form page
    } else if (!$type.length) {
        if (pk !== 'location') { listenForLocationUpdates(pk); }
    }
    // show existing indoor
    if ($floorplan.val()) {
        $indoor.show();
        if ($floorplanSelection.val()) {
            $indoorRows.show();
            $floorplanSelectionRow.hide();
        }
    // adding indoor
    } else if ($type.val() === 'indoor') {
        $indoor.show();
        $indoorRows.show();
        indoorForm($locationSelection.val());
    }

    window.geocodeApi = window.location.origin + '/admin/django_loci/location/geocode/';
    window.reverseApi = window.location.origin + '/admin/django_loci/location/reverse-geocode/';
    window.setTimeout(function () {
        window.addressLat = null;
        window.addressLng = null;
        window.receivedAlert = false;
        window.skipGeocode = 0;  // amount of times geocode operation should be not executed
        window.markerCoords = getMarker() !== undefined ? getMarker().getLatLng() : null;
        $addressInput.change(function () {
            if ($addressInput.val().length >= 10) {
                updateMap(window.geocodeApi);
            }
        });
        var timeout = null;
        $addressInput.keyup(function () {
            window.clearTimeout(timeout);
            timeout = window.setTimeout(function () {
                if ($addressInput.val().length >= 10) {
                    updateMap(window.geocodeApi);
                }
            }, 1000);
        });

        window.setInterval(function () {
            var currentMarkerCoords = getMarker() !== undefined ? getMarker().getLatLng() : null;
            var currentMarkerLat = getMarker() !== undefined ? getMarker().getLatLng().lat : null;
            var currentMarkerLng = getMarker() !== undefined ? getMarker().getLatLng().lng : null;
            if (currentMarkerCoords !== null && window.markerCoords === null && !$addressInput.val()) {
                window.markerCoords = currentMarkerCoords;
                var reverseApiWithData = window.reverseApi + '?lat=' + currentMarkerLat + '&lng=' + currentMarkerLng;
                window.fetch(reverseApiWithData)
                    .then(function (resp) {
                        var dataPromise = resp.json();
                        dataPromise.then(function (data) {
                            if (resp.status === 200) {
                                $addressInput.val(data.address);
                            } else {
                                var message = 'We couldn\'t find a related address to the location '
                                        + 'selected on the map, please enter the address manually';
                                alert(message);
                                window.skipGeocode = 2;
                            }
                        });
                    });
            }
            if (getMarker() !== undefined) {
                if (getMarker().dragging._enabled === true) {
                    window.update = true;
                    updateAdress();
                } else {
                    window.beforeEditLat = currentMarkerLat;
                    window.beforeEditLng = currentMarkerLng;
                }
            }
        }, 500);

        var submit = false;
        $form.submit(async function (e) {
            var currentMarkerCoords = getMarker() !== undefined ? getMarker().getLatLng() : null;
            var currentMarkerLat = getMarker() !== undefined ? getMarker().getLatLng().lat : null;
            var currentMarkerLng = getMarker() !== undefined ? getMarker().getLatLng().lng : null;
            if (currentMarkerCoords !== window.markerCoords && currentMarkerCoords !== null &&
                    getMarker().dragging._enabled !== true) {
                var reverseApiWithData = window.reverseApi + '?lat=' + currentMarkerLat + '&lng=' + currentMarkerLng;
                if ($addressInput.val()) {
                    var promise = window.fetch(reverseApiWithData);
                    if (currentMarkerLat !== window.addressLat ||
                            currentMarkerLng !== window.addressLng) {
                        if (window.confirm('Would you like to update address?')) {
                            var address;
                            var resp = await promise;
                            var respJson = resp.json();
                            await respJson.then(function (data) {address = data.address })
                            if (resp.status === 200) {
                                $.when($addressInput.val(address)).then(function() {
                                    submit = true;
                                    $form.submit();
                                });
                            } else {
                                var message = 'We couldn\'t find a related address to the location '
                                + 'selected on the map, please enter the address manually';
                                alert(message);
                                window.skipGeocode = 2;
                            }
                        } else {
                            submit = true;
                        }
                    } else {
                        submit = true;
                        $form.submit();
                    }
                } else {
                    $.getJSON(reverseApiWithData, function (data) {
                        $addressInput.val(data.address);
                        submit = true;
                        $form.submit();
                    });
                }
                window.markerCoords = currentMarkerCoords;
            } else if ($addressInput.val() && getMarker() === undefined) {
                $.getJSON(window.geocodeApi + '?address=' + $addressInput.val(), function (data) {
                    var geojson = '{ "type": "Point", "coordinates": [ ' +
                            data.lng.toString() + ', ' +
                            data.lat.toString() + '] }';
                    $mapGeojsonTextarea.val(geojson);
                    submit = true;
                    $form.submit();
                });
            } else {
                submit = true;
            }
            if (!submit) {
                e.preventDefault();
            }
        });
    }, 100);
});
