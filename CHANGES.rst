Changelog
=========

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
