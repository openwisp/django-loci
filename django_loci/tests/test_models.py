from django.core.exceptions import ValidationError
from django.test import TestCase

from django.contrib.auth import get_user_model

from ..models import Location, FloorPlan, ObjectLocation

User = get_user_model()


class TestModels(TestCase):
    """
    tests for django_loci.models
    """
    def _create_object(self):
        return User.objects.create(username='tester',
                                   password='tester',
                                   email='test@test.com')

    def _create_location(self, **kwargs):
        options = dict(name='test-location',
                       address='Via del Corso, Roma',
                       geometry='SRID=4326;POINT (12.019043 42.277309)')
        options.update(kwargs)
        l = Location(**options)
        l.full_clean()
        l.save()
        return l

    def test_location_str(self):
        l = Location(name='test-location')
        self.assertEqual(str(l), l.name)

    def test_floorplan_str(self):
        l = self._create_location()
        fl = FloorPlan(location=l, floor=2)
        self.assertEqual(str(fl), 'test-location 2nd floor')

    def test_object_location_clean_location(self):
        l1 = self._create_location()
        l2 = self._create_location()
        fl2 = FloorPlan(location=l2, floor=1, image='dummy.jpg')
        fl2.save()
        user = self._create_object()
        ol = ObjectLocation(content_object=user,
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
