import json

from django import forms
from django.conf.urls import url
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from leaflet.admin import LeafletGeoAdmin

from openwisp_utils.admin import TimeReadonlyAdminMixin

from ..base.geocoding_views import geocode_view, reverse_geocode_view
from ..fields import GeometryField
from ..widgets import FloorPlanWidget, ImageWidget
from .models import AbstractLocation


class AbstractFloorPlanForm(forms.ModelForm):
    class Meta:
        exclude = tuple()
        widgets = {'image': ImageWidget()}

    class Media:
        css = {'all': ('django-loci/css/loci.css',)}


class AbstractFloorPlanAdmin(TimeReadonlyAdminMixin, admin.ModelAdmin):
    list_display = ['__str__', 'location', 'floor', 'created', 'modified']
    list_select_related = ['location']
    search_fields = ['location__name']
    raw_id_fields = ['location']
    save_on_top = True


class AbstractLocationForm(forms.ModelForm):
    class Meta:
        exclude = tuple()

    class Media:
        js = ('admin/js/jquery.init.js',
              'django-loci/js/loci.js',
              'django-loci/js/floorplan-inlines.js',)
        css = {'all': ('django-loci/css/loci.css',)}


class AbstractFloorPlanInline(TimeReadonlyAdminMixin, admin.StackedInline):
    extra = 0
    ordering = ('floor',)


class AbstractLocationAdmin(TimeReadonlyAdminMixin, LeafletGeoAdmin):
    list_display = ['name', 'short_type', 'is_mobile', 'created', 'modified']
    search_fields = ['name', 'address']
    list_filter = ['type', 'is_mobile']
    save_on_top = True

    def get_urls(self):
        # hardcoding django_loci as the prefix for the
        # view names makes it much easier to extend
        # without having to change templates
        app_label = 'django_loci'
        return [
            url(r'^(?P<pk>[^/]+)/json/$',
                self.admin_site.admin_view(self.json_view),
                name='{0}_location_json'.format(app_label)),
            url(r'^(?P<pk>[^/]+)/floorplans/json/$',
                self.admin_site.admin_view(self.floorplans_json_view),
                name='{0}_location_floorplans_json'.format(app_label)),
            url(r'^geocode/$',
                self.admin_site.admin_view(geocode_view),
                name='{0}_location_geocode_api'.format(app_label)),
            url(r'^reverse-geocode/$',
                self.admin_site.admin_view(reverse_geocode_view),
                name='{0}_location_reverse_geocode_api'.format(app_label)),
        ] + super().get_urls()

    def json_view(self, request, pk):
        instance = get_object_or_404(self.model, pk=pk)
        return JsonResponse({
            'name': instance.name,
            'type': instance.type,
            'is_mobile': instance.is_mobile,
            'address': instance.address,
            'geometry': json.loads(instance.geometry.json)
        })

    def floorplans_json_view(self, request, pk):
        instance = get_object_or_404(self.model, pk=pk)
        choices = []
        for floorplan in instance.floorplan_set.all():
            choices.append({
                'id': floorplan.pk,
                'str': str(floorplan),
                'floor': floorplan.floor,
                'image': floorplan.image.url,
                'image_width': floorplan.image.width,
                'image_height': floorplan.image.height,
            })
        return JsonResponse({'choices': choices})


class UnvalidatedChoiceField(forms.ChoiceField):
    """
    skips ChoiceField validation to allow custom options
    """
    def validate(self, value):
        super(forms.ChoiceField, self).validate(value)


_get_field = AbstractLocation._meta.get_field


class AbstractObjectLocationForm(forms.ModelForm):
    FORM_CHOICES = (
        ('', _('--- Please select an option ---')),
        ('new', _('New')),
        ('existing', _('Existing'))
    )
    LOCATION_TYPES = (
        FORM_CHOICES[0],
        AbstractLocation.LOCATION_TYPES[0],
        AbstractLocation.LOCATION_TYPES[1]
    )
    location_selection = forms.ChoiceField(choices=FORM_CHOICES, required=False)
    name = forms.CharField(label=_('Location name'),
                           max_length=75, required=False,
                           help_text=_get_field('name').help_text)
    address = forms.CharField(max_length=128, required=False)
    type = forms.ChoiceField(choices=LOCATION_TYPES, required=True,
                             help_text=_get_field('type').help_text)
    is_mobile = forms.BooleanField(label=_get_field('is_mobile').verbose_name,
                                   help_text=_get_field('is_mobile').help_text,
                                   required=False)
    geometry = GeometryField(required=False)
    floorplan_selection = forms.ChoiceField(required=False,
                                            choices=FORM_CHOICES)
    floorplan = UnvalidatedChoiceField(choices=((None, FORM_CHOICES[0][1]),),
                                       required=False)
    floor = forms.IntegerField(required=False)
    image = forms.ImageField(required=False,
                             widget=ImageWidget(thumbnail=False),
                             help_text=_('floor plan image'))
    indoor = forms.CharField(max_length=64, required=False,
                             label=_('indoor position'),
                             widget=FloorPlanWidget)

    class Meta:
        exclude = tuple()

    class Media:
        js = ('admin/js/jquery.init.js',
              'django-loci/js/loci.js',)
        css = {'all': ('django-loci/css/loci.css',)}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # set initial values for custom fields
        initial = {}
        obj = self.instance
        location = obj.location
        floorplan = obj.floorplan
        if location:
            initial.update({
                'location_selection': 'existing',
                'type': location.type,
                'is_mobile': location.is_mobile,
                'name': location.name,
                'address': location.address,
                'geometry': location.geometry,
            })
        if floorplan:
            initial.update({
                'floorplan_selection': 'existing',
                'floorplan': floorplan.pk,
                'floor': floorplan.floor,
                'image': floorplan.image
            })
            floorplan_choices = self.fields['floorplan'].choices
            self.fields['floorplan'].choices = floorplan_choices + [(floorplan.pk, floorplan)]
        self.initial.update(initial)

    @cached_property
    def floorplan_model(self):
        return self.Meta.model.floorplan.field.remote_field.model

    @cached_property
    def location_model(self):
        return self.Meta.model.location.field.remote_field.model

    def clean_floorplan(self):
        floorplan_model = self.floorplan_model
        type_ = self.cleaned_data.get('type')
        floorplan_selection = self.cleaned_data.get('floorplan_selection')
        if type_ != 'indoor' or floorplan_selection == 'new':
            return None
        pk = self.cleaned_data['floorplan']
        if not pk:
            raise ValidationError(_('No floorplan selected'))
        try:
            fl = floorplan_model.objects.get(pk=pk)
        except floorplan_model.DoesNotExist:
            raise ValidationError(_('Selected floorplan does not exist'))
        if fl.location != self.cleaned_data['location']:
            raise ValidationError(_('This floorplan is associated to a different location'))
        return fl

    def clean(self):
        data = self.cleaned_data
        type_ = data.get('type')
        is_mobile = data['is_mobile']
        msg = _('this field is required for locations of type %(type)s')
        fields = []
        if not is_mobile and type_ in ['outdoor', 'indoor']:
            fields += ['location_selection', 'name', 'address', 'geometry']
        if not is_mobile and type_ == 'indoor':
            fields += ['floorplan_selection', 'floor', 'indoor']
            if data.get('floorplan_selection') == 'existing':
                fields.append('floorplan')
            elif data.get('floorplan_selection') == 'new':
                fields.append('image')
        elif is_mobile and not data.get('location'):
            data['name'] = ''
            data['address'] = ''
            data['geometry'] = ''
            data['location_selection'] = 'new'
        for field in fields:
            if field in data and data[field] in [None, '']:
                params = {'type': type_}
                err = ValidationError(msg, params=params)
                self.add_error(field, err)

    def _get_location_instance(self):
        data = self.cleaned_data
        location = data.get('location') or self.location_model()
        location.type = data.get('type') or location.type
        location.is_mobile = data.get('is_mobile') or location.is_mobile
        location.name = data.get('name') or location.name
        location.address = data.get('address') or location.address
        location.geometry = data.get('geometry') or location.geometry
        return location

    def _get_floorplan_instance(self):
        data = self.cleaned_data
        instance = self.instance
        floorplan = data.get('floorplan') or self.floorplan_model()
        floorplan.location = instance.location
        floor = data.get('floor')
        floorplan.floor = floor if floor is not None else floorplan.floor
        # the image path is updated only during creation
        # or if the image has been actually changed
        if data.get('image') and self.initial.get('image') != data.get('image'):
            floorplan.image = data['image']
        return floorplan

    def save(self, commit=True):
        instance = self.instance
        data = self.cleaned_data
        # create or update location
        instance.location = self._get_location_instance()
        # set name of mobile locations automatically
        if data['is_mobile'] and not instance.location.name:
            instance.location.name = str(self.instance.content_object)
        instance.location.save()
        # create or update floorplan
        if data['type'] == 'indoor':
            instance.floorplan = self._get_floorplan_instance()
            instance.floorplan.save()
        # call super
        return super().save(commit=True)


class ObjectLocationMixin(TimeReadonlyAdminMixin):
    """
    Base ObjectLocationInline logic, can be imported and
    mixed in with different inline classes (stacked, tabular).
    If you need the generic inline look below.
    """
    verbose_name = _('geographic information')
    verbose_name_plural = verbose_name
    raw_id_fields = ('location',)
    max_num = 1
    extra = 1
    template = 'admin/django_loci/location_inline.html'
    fieldsets = (
        (None, {'fields': ('location_selection',)}),
        ('Geographic coordinates', {
            'classes': ('loci', 'coords'),
            'fields': ('location', 'type', 'is_mobile',
                       'name', 'address', 'geometry'),
        }),
        ('Indoor coordinates', {
            'classes': ('indoor', 'coords'),
            'fields': ('floorplan_selection', 'floorplan',
                       'floor', 'image', 'indoor',),
        })
    )


class AbstractObjectLocationInline(ObjectLocationMixin, GenericStackedInline):
    """
    Generic Inline + ObjectLocationMixin
    """
    pass
