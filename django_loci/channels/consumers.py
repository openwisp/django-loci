from ..models import Location
from .base import BaseLocationBroadcast


class LocationBroadcast(BaseLocationBroadcast):
    model = Location
