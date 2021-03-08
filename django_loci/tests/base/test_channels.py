# use pytest
import importlib

import pytest
from channels.db import database_sync_to_async
from channels.routing import ProtocolTypeRouter
from channels.testing import WebsocketCommunicator
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import Permission
from django.http.request import HttpRequest

from django_loci.channels.consumers import LocationBroadcast

from ...channels.base import _get_object_or_none
from .. import TestAdminMixin, TestLociMixin


class BaseTestChannels(TestAdminMixin, TestLociMixin):
    """
    In channels 2.x, Websockets can only be tested
    asynchronously, hence, pytest is used for these tests.
    """

    def _force_login(self, user, backend=None):
        engine = importlib.import_module(settings.SESSION_ENGINE)
        request = HttpRequest()
        request.session = engine.SessionStore()
        login(request, user, backend)
        request.session.save
        return request.session

    async def _get_request_dict(self, pk=None, user=None):
        if not pk:
            location = await database_sync_to_async(self._create_location)(
                is_mobile=True
            )
            await database_sync_to_async(self._create_object_location)(
                location=location
            )
            pk = location.pk
        path = '/ws/loci/location/{0}/'.format(pk)
        session = None
        if user:
            session = await database_sync_to_async(self._force_login)(user)
        return {'pk': pk, 'path': path, 'session': session}

    def _get_communicator(self, request_vars, user=None):
        communicator = WebsocketCommunicator(
            LocationBroadcast.as_asgi(), request_vars['path']
        )
        if user:
            communicator.scope.update(
                {
                    "user": user,
                    "session": request_vars['session'],
                    "url_route": {"kwargs": {"pk": request_vars['pk']}},
                }
            )
        return communicator

    @pytest.mark.django_db(transaction=True)
    def test_object_or_none(self):
        result = _get_object_or_none(self.location_model, pk=1)
        assert result is None
        plausible_pk = self.location_model().pk
        result = _get_object_or_none(self.location_model, pk=plausible_pk)
        assert result is None

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    async def test_consumer_unauthenticated(self):
        request_vars = await self._get_request_dict()
        communicator = WebsocketCommunicator(
            LocationBroadcast.as_asgi(), request_vars['path']
        )
        connected, _ = await communicator.connect()
        assert not connected
        await communicator.disconnect()

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    async def test_connect_admin(self):
        test_user = await database_sync_to_async(self._create_admin)()
        request_vars = await self._get_request_dict(user=test_user)
        communicator = self._get_communicator(request_vars, test_user)
        connected, _ = await communicator.connect()
        assert connected
        await communicator.disconnect()

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    async def test_consumer_not_staff(self):
        test_user = await database_sync_to_async(self.user_model.objects.create_user)(
            username='user', password='password', email='test@test.org'
        )
        request_vars = await self._get_request_dict(user=test_user)
        communicator = self._get_communicator(request_vars, test_user)
        connected, _ = await communicator.connect()
        assert not connected
        await communicator.disconnect()

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    async def test_consumer_404(self):
        pk = self.location_model().pk
        admin = await database_sync_to_async(self._create_admin)()
        request_vars = await self._get_request_dict(pk=pk, user=admin)
        communicator = self._get_communicator(request_vars, admin)
        connected, _ = await communicator.connect()
        assert not connected

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    async def test_consumer_staff_but_no_change_permission(self):
        test_user = await database_sync_to_async(self.user_model.objects.create_user)(
            username='user', password='password', email='test@test.org', is_staff=True
        )
        location = await database_sync_to_async(self._create_location)(is_mobile=True)
        ol = await database_sync_to_async(self._create_object_location)(
            location=location
        )
        pk = ol.location.pk
        request_vars = await self._get_request_dict(pk=pk, user=test_user)
        communicator = self._get_communicator(request_vars, test_user)
        connected, _ = await communicator.connect()
        assert not connected
        await communicator.disconnect()
        # add permission to change location and repeat
        loc_perm = await database_sync_to_async(
            (
                await database_sync_to_async(Permission.objects.filter)(
                    name='Can change location'
                )
            ).first
        )()
        await database_sync_to_async(test_user.user_permissions.add)(loc_perm)
        test_user = await database_sync_to_async(self.user_model.objects.get)(
            pk=test_user.pk
        )
        communicator = self._get_communicator(request_vars, test_user)
        connected, _ = await communicator.connect()
        assert connected
        await communicator.disconnect()

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    async def test_location_update(self):
        test_user = await database_sync_to_async(self._create_admin)()
        request_vars = await self._get_request_dict(user=test_user)
        communicator = self._get_communicator(request_vars, test_user)
        connected, _ = await communicator.connect()
        assert connected
        await database_sync_to_async(self._save_location)(request_vars['pk'])
        response = await communicator.receive_json_from()
        assert response == {'type': 'Point', 'coordinates': [12.513124, 41.897903]}
        await communicator.disconnect()

    def _save_location(self, pk):
        loc = self.location_model.objects.get(pk=pk)
        loc.geometry = 'POINT (12.513124 41.897903)'
        loc.save()

    def test_routing(self):
        from django_loci.channels.asgi import channel_routing

        assert isinstance(channel_routing, ProtocolTypeRouter)
