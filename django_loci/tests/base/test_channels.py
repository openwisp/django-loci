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

from django_loci.channels.consumers import CommonLocationBroadcast, LocationBroadcast

from ...channels.base import _get_object_or_none
from .. import TestAdminMixin, TestLociMixin


class BaseTestChannels(TestAdminMixin, TestLociMixin):
    """
    In channels 2.x, Websockets can only be tested
    asynchronously, hence, pytest is used for these tests.
    """

    async def _force_login(self, user, backend=None):
        engine = importlib.import_module(settings.SESSION_ENGINE)
        request = HttpRequest()
        request.session = engine.SessionStore()
        database_sync_to_async(login)(request, user, backend)
        request.session.save
        return request.session

    async def _get_specific_location_request_dict(self, pk=None, user=None):
        if not pk:
            location = await database_sync_to_async(self._create_location)(
                is_mobile=True
            )
            await database_sync_to_async(self._create_object_location)(
                location=location
            )
            pk = location.pk
        path = "/ws/loci/location/{0}/".format(pk)
        session = None
        if user:
            session = await self._force_login(user)
        return {"pk": pk, "path": path, "session": session}

    async def _get_common_location_request_dict(self, user=None):
        location = await database_sync_to_async(self._create_location)(is_mobile=True)
        await database_sync_to_async(self._create_object_location)(location=location)
        pk = location.pk
        path = "/ws/loci/locations/"
        session = None
        if user:
            session = await self._force_login(user)
        return {"pk": pk, "path": path, "session": session}

    def _get_location_communicator(
        self, consumer_cls, request_vars, user=None, include_pk=False
    ):
        communicator = WebsocketCommunicator(
            consumer_cls.as_asgi(), request_vars["path"]
        )
        if user:
            scope = {
                "user": user,
                "session": request_vars["session"],
            }
            if include_pk:
                scope["url_route"] = {"kwargs": {"pk": request_vars["pk"]}}
            communicator.scope.update(scope)
        return communicator

    def _get_specific_location_communicator(self, request_vars, user=None):
        return self._get_location_communicator(
            LocationBroadcast, request_vars, user=user, include_pk=True
        )

    def _get_common_location_communicator(self, request_vars, user=None):
        return self._get_location_communicator(
            CommonLocationBroadcast, request_vars, user=user, include_pk=False
        )

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
        request_vars = await self._get_specific_location_request_dict()
        communicator = self._get_specific_location_communicator(request_vars)
        connected, _ = await communicator.connect()
        assert not connected
        await communicator.disconnect()

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    async def test_common_location_consumer_unauthenticated(self):
        request_vars = await self._get_common_location_request_dict()
        communicator = self._get_common_location_communicator(request_vars)
        connected, _ = await communicator.connect()
        assert not connected
        await communicator.disconnect()

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    async def test_connect_admin(self):
        test_user = await database_sync_to_async(self._create_admin)()
        request_vars = await self._get_specific_location_request_dict(user=test_user)
        communicator = self._get_specific_location_communicator(request_vars, test_user)
        connected, _ = await communicator.connect()
        assert connected
        await communicator.disconnect()

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    async def test_common_location_connect_admin(self):
        test_user = await database_sync_to_async(self._create_admin)()
        request_vars = await self._get_common_location_request_dict(user=test_user)
        communicator = self._get_common_location_communicator(request_vars, test_user)
        connected, _ = await communicator.connect()
        assert connected
        await communicator.disconnect()

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    async def test_consumer_not_staff(self):
        test_user = await database_sync_to_async(self.user_model.objects.create_user)(
            username="user", password="password", email="test@test.org"
        )
        request_vars = await self._get_specific_location_request_dict(user=test_user)
        communicator = self._get_specific_location_communicator(request_vars, test_user)
        connected, _ = await communicator.connect()
        assert not connected
        await communicator.disconnect()

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    async def test_common_location_consumer_not_staff(self):
        test_user = await database_sync_to_async(self.user_model.objects.create_user)(
            username="user", password="password", email="test@test.org"
        )
        request_vars = await self._get_common_location_request_dict(user=test_user)
        communicator = self._get_common_location_communicator(request_vars, test_user)
        connected, _ = await communicator.connect()
        assert not connected
        await communicator.disconnect()

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    async def test_consumer_404(self):
        pk = self.location_model().pk
        admin = await database_sync_to_async(self._create_admin)()
        request_vars = await self._get_specific_location_request_dict(pk=pk, user=admin)
        communicator = self._get_specific_location_communicator(request_vars, admin)
        connected, _ = await communicator.connect()
        assert not connected

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    async def test_consumer_staff_but_no_change_permission(self):
        test_user = await database_sync_to_async(self.user_model.objects.create_user)(
            username="user", password="password", email="test@test.org", is_staff=True
        )
        location = await database_sync_to_async(self._create_location)(is_mobile=True)
        ol = await database_sync_to_async(self._create_object_location)(
            location=location
        )
        pk = ol.location.pk
        request_vars = await self._get_specific_location_request_dict(
            pk=pk, user=test_user
        )
        communicator = self._get_specific_location_communicator(request_vars, test_user)
        connected, _ = await communicator.connect()
        assert not connected
        await communicator.disconnect()

        # add permission to change location and repeat
        loc_perm = await Permission.objects.filter(
            codename=f"change_{self.location_model._meta.model_name}"
        ).afirst()
        await test_user.user_permissions.aadd(loc_perm)
        test_user = await self.user_model.objects.aget(pk=test_user.pk)
        communicator = self._get_specific_location_communicator(request_vars, test_user)
        connected, _ = await communicator.connect()
        assert connected
        await communicator.disconnect()

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    async def test_common_location_consumer_staff_but_no_change_permission(self):
        test_user = await database_sync_to_async(self.user_model.objects.create_user)(
            username="user", password="password", email="test@test.org", is_staff=True
        )
        location = await database_sync_to_async(self._create_location)(is_mobile=True)
        await database_sync_to_async(self._create_object_location)(location=location)
        request_vars = await self._get_common_location_request_dict(user=test_user)
        communicator = self._get_common_location_communicator(request_vars, test_user)
        connected, _ = await communicator.connect()
        assert not connected
        await communicator.disconnect()
        # add permission to change location and repeat
        loc_perm = await Permission.objects.filter(
            codename=f"change_{self.location_model._meta.model_name}"
        ).afirst()
        await test_user.user_permissions.aadd(loc_perm)
        test_user = await self.user_model.objects.aget(pk=test_user.pk)
        communicator = self._get_common_location_communicator(request_vars, test_user)
        connected, _ = await communicator.connect()
        assert connected
        await communicator.disconnect()

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    async def test_location_update(self):
        test_user = await database_sync_to_async(self._create_admin)()
        request_vars = await self._get_specific_location_request_dict(user=test_user)
        communicator = self._get_specific_location_communicator(request_vars, test_user)
        connected, _ = await communicator.connect()
        assert connected
        await self._save_location(request_vars["pk"])
        response = await communicator.receive_json_from()
        assert response == {
            "geometry": {"type": "Point", "coordinates": [12.513124, 41.897903]},
            "address": "Via del Corso, Roma, Italia",
        }
        await communicator.disconnect()

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    async def test_common_location_update(self):
        test_user = await database_sync_to_async(self._create_admin)()
        request_vars = await self._get_common_location_request_dict(user=test_user)
        communicator = self._get_common_location_communicator(request_vars, test_user)
        connected, _ = await communicator.connect()
        assert connected
        await self._save_location(request_vars["pk"])
        response = await communicator.receive_json_from()
        assert response == {
            "id": str(request_vars["pk"]),
            "geometry": {"type": "Point", "coordinates": [12.513124, 41.897903]},
            "address": "Via del Corso, Roma, Italia",
            "name": "test-location",
            "type": "outdoor",
            "is_mobile": True,
        }
        await communicator.disconnect()

    async def _save_location(self, pk):
        loc = await self.location_model.objects.aget(pk=pk)
        loc.geometry = "POINT (12.513124 41.897903)"
        await loc.asave()

    def test_routing(self):
        from django_loci.channels.asgi import channel_routing

        assert isinstance(channel_routing, ProtocolTypeRouter)
