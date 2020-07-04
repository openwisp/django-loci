import pytest


@pytest.fixture(scope='session')
def django_db_modify_db_settings():
    """ used to speed up pytest with django """
    pass
