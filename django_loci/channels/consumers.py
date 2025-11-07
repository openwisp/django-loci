from ..models import Location
from .base import BaseLocationBroadcast, BaseAllLocationBroadcast


class LocationBroadcast(BaseLocationBroadcast):
    model = Location

class AllLocationBroadcast(BaseAllLocationBroadcast):
    model = Location
