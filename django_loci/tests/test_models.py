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

    def test_object_location_clean_location(self):
        l1 = self._create_location()
        l2 = self._create_location()
        fl2 = self._create_floorplan(location=l2)
        obj = self._create_object()
        ol = self.object_location_model(content_object=obj,
                                        type='indoor',
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

    def test_delete(self):
        loc = self._create_location()
        obj = self._create_object()
        ol = self.object_location_model(content_object=obj,
                                        type='mobile',
                                        location=loc)
        ol.full_clean()
        ol.save()
        ol.delete()
        self.assertEqual(self.location_model.objects.filter(id=loc.id).count(), 0)

    def test_floorplan_image(self):
        fl = self._create_floorplan()
        path = fl.image.file.name
        name = path.split('/')[-1]
        self.assertEqual(name, '{0}.jpg'.format(fl.id))
        # overwrite
        fl.image = self._get_simpleuploadedfile()
        fl.full_clean()
        fl.save()
        self.assertEqual(name, '{0}.jpg'.format(fl.id))
        # delete
        fl.delete()
        self.assertFalse(os.path.isfile(path))
