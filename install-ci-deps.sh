#!/bin/bash
# Install geospatial and Python dependencies for the selected Django version.
set -e
if [ "${CI_SYSTEM_DEPS_READY:-0}" != 1 ]; then
    sudo apt update
    sudo apt-get -qq -y install sqlite3 libsqlite3-dev libsqlite3-mod-spatialite gdal-bin
    sudo npm install -g prettier
fi
if [ "${CI_SYSTEM_DEPS_ONLY:-0}" = 1 ]; then
    exit 0
fi
python -m pip install -U -r requirements-test.txt
python -m pip install -U -e .
python -m pip install -U "${DJANGO_VERSION:?Set DJANGO_VERSION to a CI matrix value}"
