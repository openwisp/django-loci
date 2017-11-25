django-loci
===========

.. image:: https://travis-ci.org/openwisp/django-loci.svg
   :target: https://travis-ci.org/openwisp/django-loci

.. image:: https://coveralls.io/repos/openwisp/django-loci/badge.svg
  :target: https://coveralls.io/r/openwisp/django-loci

.. image:: https://requires.io/github/openwisp/django-loci/requirements.svg?branch=master
   :target: https://requires.io/github/openwisp/django-loci/requirements/?branch=master
   :alt: Requirements Status

.. image:: https://badge.fury.io/py/django-loci.svg
   :target: http://badge.fury.io/py/django-loci

------------

TODO

------------

.. contents:: **Table of Contents**:
   :backlinks: none
   :depth: 3

------------

Dependencies
------------

* Python 2.7 or Python >= 3.4
* one of the databases supported by GeoDjango

Install stable version from pypi
--------------------------------

Install from pypi:

.. code-block:: shell

    pip install django-loci

Install development version
---------------------------

Install tarball:

.. code-block:: shell

    pip install https://github.com/openwisp/django-loci/tarball/master

Alternatively you can install via pip using git:

.. code-block:: shell

    pip install -e git+git://github.com/openwisp/django-loci#egg=django_loci

If you want to contribute, install your cloned fork:

.. code-block:: shell

    git clone git@github.com:<your_fork>/django-loci.git
    cd django_loci
    python setup.py develop

Setup (integrate in an existing django project)
-----------------------------------------------

Add ``django_loci`` and its dependencies to `INSTALLED_APPS`` in the following order:

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        'django.contrib.gis',
        'django_loci',
        'django.contrib.admin',
        'leaflet',
        'channels'
        # ...
    ]

Now run migrations:

.. code-block:: shell

    ./manage.py migrate

Settings
--------

``LOCI_FLOORPLAN_STORAGE``
~~~~~~~~~~~~~~~~~~~~~~~~~~

+--------------+-------------------------------------------+
| **type**:    | ``str``                                   |
+--------------+-------------------------------------------+
| **default**: | ``django_loci.storage.OverwriteStorage``  |
+--------------+-------------------------------------------+

The django file storage class used for uploading floorplan images.

The filestorage can be changed to a different one as long as it has an
``upload_to`` class method which will be passed to ``FloorPlan.image.upload_to``.

To understand the details of this statement, take a look at the code of
`django_loci.storage.OverwriteStorage
<https://github.com/openwisp/django-loci/blob/master/django_loci/storage.py>`_.

Installing for development
--------------------------

Install sqlite:

.. code-block:: shell

    sudo apt-get install sqlite3 libsqlite3-dev libsqlite3-mod-spatialite

Install your forked repo:

.. code-block:: shell

    git clone git://github.com/<your_fork>/django-loci
    cd django-loci/
    python setup.py develop

Install test requirements:

.. code-block:: shell

    pip install -r requirements-test.txt

Create database:

.. code-block:: shell

    cd tests/
    ./manage.py migrate
    ./manage.py createsuperuser

Launch development server and SMTP debugging server:

.. code-block:: shell

    ./manage.py runserver

You can access the admin interface at http://127.0.0.1:8000/admin/.

Run tests with:

.. code-block:: shell

    ./runtests.py

Contributing
------------

1. Announce your intentions in the `OpenWISP Mailing List <https://groups.google.com/d/forum/openwisp>`_
2. Fork this repo and install it
3. Follow `PEP8, Style Guide for Python Code`_
4. Write code
5. Write tests for your code
6. Ensure all tests pass
7. Ensure test coverage does not decrease
8. Document your changes
9. Send pull request

.. _PEP8, Style Guide for Python Code: http://www.python.org/dev/peps/pep-0008/

Changelog
---------

See `CHANGES <https://github.com/openwisp/django-loci/blob/master/CHANGES.rst>`_.

License
-------

See `LICENSE <https://github.com/openwisp/django-loci/blob/master/LICENSE>`_.
