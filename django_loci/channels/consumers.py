from ..models import Location
from .base import BaseAllLocationBroadcast, BaseLocationBroadcast


class LocationBroadcast(BaseLocationBroadcast):
    model = Location


class AllLocationBroadcast(BaseAllLocationBroadcast):
    model = Location
