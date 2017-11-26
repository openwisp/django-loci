from .base import BaseLocationBroadcast
from ..models import Location


class LocationBroadcast(BaseLocationBroadcast):
    model = Location
