from django.http import JsonResponse
from django.utils.module_loading import import_string
from geopy.extra.rate_limiter import RateLimiter

from ..settings import (DJANGO_LOCI_GEOCODE_API_KEY, DJANGO_LOCI_GEOCODE_FAILURE_DELAY,
                        DJANGO_LOCI_GEOCODE_RETRIES, DJANGO_LOCI_GEOCODER)

geocoder = import_string('geopy.geocoders.{}'.format(DJANGO_LOCI_GEOCODER))
if DJANGO_LOCI_GEOCODER != 'GoogleV3':
    geolocator = geocoder(user_agent="django_loci")
else:
    geolocator = geocoder(api_key=DJANGO_LOCI_GEOCODE_API_KEY)  # pragma: nocover
geocode = RateLimiter(geolocator.geocode,
                      max_retries=DJANGO_LOCI_GEOCODE_RETRIES,
                      error_wait_seconds=DJANGO_LOCI_GEOCODE_FAILURE_DELAY)
reverse_geocode = RateLimiter(geolocator.reverse,
                              max_retries=DJANGO_LOCI_GEOCODE_RETRIES,
                              error_wait_seconds=DJANGO_LOCI_GEOCODE_FAILURE_DELAY)


def geocode_view(request):
    address = request.GET.get('address')
    if address is None:
        return JsonResponse({'error': 'Address parameter not defined'}, status=400)
    else:
        location = geocode(address)
        if location is None:
            return JsonResponse({'error': 'Not found location with given name'}, status=404)
        else:
            lat = location.latitude
            lng = location.longitude
    return JsonResponse({
        'lat': lat,
        'lng': lng,
    })


def reverse_geocode_view(request):
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    if lat and lng:
        location = reverse_geocode((lat, lng))
        if location is None:
            return JsonResponse({'address': ''}, status=404)
        else:
            if DJANGO_LOCI_GEOCODER != 'GoogleV3':
                address = location.address
            else:
                address = str(location[0].address)  # pragma: nocover
    else:
        return JsonResponse({'error': 'lat or lng parameter not defined'}, status=400)
    return JsonResponse({
        'address': address
    })
