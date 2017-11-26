from channels.test import WSClient

from .. import TestAdminMixin, TestLociMixin
from ...channels.base import _get_object_or_none


class BaseTestChannels(TestAdminMixin, TestLociMixin):
    def setUp(self):
        client = WSClient()
        self.client = client

    def test_object_or_none(self):
        result = _get_object_or_none(self.location_model, pk=1)
        self.assertEqual(result, None)
        plausible_pk = self.location_model().pk
        result = _get_object_or_none(self.location_model, pk=plausible_pk)
        self.assertEqual(result, None)

    def _test_ws_add(self, pk=None, user=None):
        if not pk:
            location = self._create_location(is_mobile=True)
            ol = self._create_object_location(location=location)
            pk = ol.location.pk
        path = '/loci/location/{0}/'.format(pk)
        if user:
            self.client.force_login(user)
        self.client.send_and_consume('websocket.connect', path=path)
        return {'ol': ol, 'path': path}

    def test_ws_add_unauthenticated(self):
        try:
            self._test_ws_add()
        except AssertionError as e:
            self.assertIn('Connection rejected', str(e))
        else:
            self.fail('AssertionError not raised')

    def test_connect_and_disconnect(self):
        res = self._test_ws_add(user=self._create_admin())
        self.assertEqual(self.client.receive(), None)
        self.client.send_and_consume('websocket.disconnect', path=res['path'])

    def test_ws_add_not_staff(self):
        user = self.user_model.objects.create_user(username='user',
                                                   password='password',
                                                   email='test@test.org')
        try:
            self._test_ws_add(user=user)
        except AssertionError as e:
            self.assertIn('Connection rejected', str(e))
        else:
            self.fail('AssertionError not raised')

    def test_ws_add_404(self):
        pk = self.location_model().pk
        admin = self._create_admin()
        try:
            self._test_ws_add(pk=pk, user=admin)
        except AssertionError as e:
            self.assertIn('Connection rejected', str(e))
        else:
            self.fail('AssertionError not raised')

    def test_location_update(self):
        res = self._test_ws_add(user=self._create_admin())
        res['ol'].location.geometry = 'POINT (12.513124 41.897903)'
        res['ol'].location.save()
        result = self.client.receive()
        self.assertIsInstance(result, dict)
        self.assertDictEqual(result, {'type': 'Point', 'coordinates': [12.513124, 41.897903]})
