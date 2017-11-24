import os

from django.core.exceptions import ValidationError
from django.test import TestCase

from . import TestLociMixin
from ..models import FloorPlan, Location, ObjectLocation
from .testdeviceapp.models import Device


class TestModels(TestLociMixin, TestCase):
    """
    tests for django_loci.models
    """
    object_model = Device
    location_model = Location
    floorplan_model = FloorPlan
    object_location_model = ObjectLocation

    def test_location_str(self):
        loc = self.location_model(name='test-location')
        self.assertEqual(str(loc), loc.name)

    def test_floorplan_str(self):
        loc = self._create_location()
        fl = self.floorplan_model(location=loc, floor=2)
        self.assertEqual(str(fl), 'test-location 2nd floor')
        fl.floor = 0
        self.assertEqual(str(fl), 'test-location ground floor')

    def test_object_location_clean_location(self):
        l1 = self._create_location(type='indoor')
        l2 = self._create_location(type='indoor')
        fl2 = self._create_floorplan(location=l2)
        obj = self._create_object()
        ol = self.object_location_model(content_object=obj,
                                        location=l1,
                                        floorplan=fl2)
        try:
            ol.full_clean()
        except ValidationError as e:
            self.assertIn('__all__', e.message_dict)
            self.assertEqual(e.message_dict.get('__all__')[0],
                             'Invalid floorplan (belongs to a different location)')
        else:
            self.fail('ValidationError not raised')

    def test_floorplan_image(self):
        fl = self._create_floorplan()
        path = fl.image.file.name.split('/')
        name = path[-1]
        dir_ = path[-2]
        self.assertEqual(name, '{0}.jpg'.format(fl.id))
        self.assertEqual(dir_, 'floorplans')
        # overwrite
        fl.image = self._get_simpleuploadedfile()
        fl.full_clean()
        fl.save()
        path = fl.image.file.name.split('/')
        name = path[-1]
        dir_ = path[-2]
        self.assertEqual(name, '{0}.jpg'.format(fl.id))
        self.assertEqual(dir_, 'floorplans')
        # delete
        fl.delete()
        self.assertFalse(os.path.isfile(fl.image.file.name))

    def test_floorplan_delete_corner_case(self):
        fl = self._create_floorplan()
        os.remove(fl.image.file.name)
        # there should be no failure
        fl.delete()

    def test_floorplan_association_validation(self):
        outdoor = self._create_location(type='outdoor')
        try:
            self._create_floorplan(location=outdoor)
        except ValidationError as e:
            err_str = str(e)
            self.assertIn('floorplans can only be associated to', err_str)
            self.assertIn('indoor', err_str)
        else:
            self.fail('ValidationError not raised')

    def test_location_change_indoor_to_outdoor(self):
        fl = self._create_floorplan()
        location = fl.location
        location.type = 'outdoor'
        try:
            location.full_clean()
        except ValidationError as e:
            self.assertIn('type', e.message_dict)
            err_str = str(e.message_dict['type'])
            self.assertIn('this location has floorplans', err_str)
            self.assertIn('please delete them', err_str)
        else:
            self.fail('ValidationError not raised')
