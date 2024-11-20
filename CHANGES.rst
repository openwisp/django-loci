Changelog
=========

Version 1.1.1 [2024-11-20]
--------------------------

- [deps] Updated django-leaflet to ~=0.31.0.

Version 1.1.0 [2024-08-16]
--------------------------

Changes
~~~~~~~

- Use ``settings.DEFAULT_STORAGE_CLASS`` as base for OverwriteStorage,
  adapting the storage backend to project settings.

**Dependencies:**

- Bumped ``django-leaflet~=0.30.1``
- Bumped ``Pillow~=10.4.0``
- Bumped ``geopy~=2.4.1``
- Bumped ``openwisp-utils~=1.1.0``
- Added support for Python ``3.10``.
- Added support for Django ``4.2``.
- Dropped support for Python ``3.7``.
- Dropped support for Django ``3.0.x``, ``3.1.x`` and ``4.0.x``.

Bugfixes
~~~~~~~~

- Fixed an issue with deleting ``FloorPlan.image`` by using the
  appropriate storage backend method.
- Resolved a bug causing outdoor locations to incorrectly appear in the
  location list when creating floorplans.

Version 1.0.1 [2022-04-20]
--------------------------

Bugfixes
~~~~~~~~

- Updated Pillow to ~=9.1.0 to fix a security CVE
- Fixed channels deprecation warning

Version 1.0.0 [2022-02-25]
--------------------------

Changes
~~~~~~~

- Converted geocoding test to check `#90
  <https://github.com/openwisp/django-loci/issues/90>`_
- Use ``ReconnectingWebsocket`` to websocket connection `#101
  <https://github.com/openwisp/django-loci/issues/101>`_
- Dropped support for Python ``3.6``
- Added support for Python ``3.8`` and ``3.9``
- Added support for Django ``3.2.x`` and ``4.0.x``
- Migrated to ``channels~=3.0.4``
- Bumped ``Pillow~=9.0.0``
- Bumped ``geopy~=2.2.0``
- Bumped ``openwisp-utils~=1.0.0``
- Set lowest django version supported to ``django~=3.0.0``

Version 0.4.3 [2021-06-29]
--------------------------

- The dependency on the Pillow library was updated to a recent version
  which was patched for security vulnerabilities
- Several other dependencies and test dependencies were updated
  (django-leaflet, geopy, pytest-django, pytest-asyncio, pytest-cov,
  responses, openwisp-utils)

Version 0.4.2 [2021-03-16]
--------------------------

- Fixed broken UI in inline geo selection flow caused by a JS change in
  django (`issue #85
  <https://github.com/openwisp/django-loci/issues/85>`_)

Version 0.4.1 [2021-02-24]
--------------------------

Bugfixes
~~~~~~~~

- Fixed the ``DJANGO_LOCI_GEOCODE_STRICT_TEST`` setting, which internally
  was using a different name, therefore the documented setting was not
  working

Version 0.4.0 [2020-11-19]
--------------------------

Features
~~~~~~~~

- [ux] Automatically fetch map coordinates from address field and vice
  versa + configurable geocoding

Changes
~~~~~~~

- [deps] Increased Pillow range to allow new 8.0.0 version
- [deps] Updated openwisp-utils version range to support 0.6 and 0.7

Bugfixes
~~~~~~~~

- [fix] Fixed integrity error in ``floorplan.floor`` when
  ``is_mobile=True``
- [fix] Fixed corner case involving restoring ``is_mobile=False``

Version 0.3.4 [2020-08-16]
--------------------------

- [deps] Added support for django 3.1
- [deps] Updated to openwisp-utils 0.6

Version 0.3.3 [2020-07-25]
--------------------------

- [fix] Fixed websocket connect error for location change view
- [deps] Added support for Pillow~=7.2.0 & openwisp-utils~=0.5.1 and
  dropped their lower versions
- [deps] Added support for django-leaflet version 0.28

Version 0.3.2 [2020-07-01]
--------------------------

- [fix] Fixed bug in floorplan fields
- [fix] Fixed bug which caused geographic map to disappears on narrow
  screens
- [fix] Fixed bug in JS logic
- [change] Allow to create an indoor location without specifying indoor
  coordinates

Version 0.3.1 [2020-01-21]
--------------------------

- Added support to django 3.0, dropped support for django versions older
  than 2.2
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
