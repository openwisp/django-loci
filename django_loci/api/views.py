# from rest_framework import generics
# from rest_framework_gis import serializers as gis_serializers
#
# from ..models import Location
#
#
# class LocationSerializer(gis_serializers.GeoFeatureModelSerializer):
#     class Meta:
#         model = Location
#         geo_field = 'geometry'
#         fields = ('id', 'name', 'geometry')
#         read_only_fields = ('name', )
#
#
# class MobileLocation(generics.RetrieveUpdateAPIView):
#     model = Location
#     serializer_class = LocationSerializer
#     queryset = Device.objects.all()
#     permission_classes = (DevicePermission,)
#
#     # TODO
#
#     def get_object(self, *args, **kwargs):
#         device = super(MobileLocation, self).get_object()
#         dl = device.devicelocation_set.select_related('location').first()
#         if dl:
#             return dl.location
#         # automatically create object
#         else:
#             # TODO: this may become a DeviceLocation model method
#             l = Location.objects.create(name=device.name,
#                                         organization=device.organization)
#             DeviceLocation.objects.create(device=device,
#                                           type='mobile',
#                                           location=l)
#             return l
#
#
#
# mobile_location = MobileLocation.as_view()
