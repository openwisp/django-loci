Changelog
=========

Version 0.3.3 [2020-07-25]
--------------------------

- [fix] Fixed websocket connect error for location change view
- [deps] Added support for Pillow~=7.2.0 & openwisp-utils~=0.5.1 and dropped their lower versions
- [deps] Added support for django-leaflet version 0.28

Version 0.3.2 [2020-07-01]
--------------------------

- [fix] Fixed bug in floorplan fields
- [fix] Fixed bug which caused geographic map to disappears on narrow screens
- [fix] Fixed bug in JS logic
- [change] Allow to create an indoor location without specifying indoor coordinates

Version 0.3.1 [2020-01-21]
--------------------------

- Added support to django 3.0, dropped support for django versions older than 2.2
- [admin] Fixed UX issue with ``is_mobile`` checkbox

Version 0.3.0 [2020-01-13]
--------------------------

- Upgraded django-channels to version 2
- Upgraded dependencies (django, django-leaflet, Pillow)
- Geometry shouldn't be allowed to be None if not mobile
- Fixed admin fields hidden by mistake in case of validation errors
- Fixed type ``KeyError`` exception during form validation

Version 0.2.1 [2018-09-02]
--------------------------

- [tests] Removed duplication of definition of floorplan test file

Version 0.2.0 [2018-02-19]
--------------------------

- [requirements] Added support for django 2.0

Version 0.1.1 [2017-12-06]
--------------------------

- [admin] Reusable foreign_key_raw_id template
- [js] Added client side validation for indoor position
- [js] Do not reset indoor form on first load
- [websockets] Do not attempt connection in location add page
- [websockets] Automatically determine ws protocol

Version 0.1.0 [2017-12-02]
--------------------------

- first release
