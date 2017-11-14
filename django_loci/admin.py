import json

from django import forms
from django.conf.urls import url
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline
from django.core.eceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from leaflet.admin import LeafletGeoAdmin

from openwisp_utils.admin import TimeReadonlyAdminMixin

from .fields import GeometryField
from .models import FloorPlan, Location, ObjectLocation
from .widgets import FloorPlanWidget, ImageWidget


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        exclude = tuple()

    class Media:
        js = ('django-loci/js/loci.js',)
        css = {'all': ('django-loci/css/loci.css',)}


class LocationAdmin(TimeReadonlyAdminMixin, LeafletGeoAdmin):
    list_display = ('name', 'created', 'modified')
    search_fields = ('name', 'address')
    save_on_top = True
    form = LocationForm

    def get_urls(self):
        app_label = self.model._meta.app_label
        return [
            url(r'^(?P<pk>[^/]+)/json/$',
                self.admin_site.admin_view(self.json_view),
                name='{0}_location_json'.format(app_label)),
            url(r'^(?P<pk>[^/]+)/floorplans/json/$',
                self.admin_site.admin_view(self.floorplans_json_view),
                name='{0}_location_floorplans_json'.format(app_label))
        ] + super(LocationAdmin, self).get_urls()

    def json_view(self, request, pk):
        instance = get_object_or_404(self.model, pk=pk)
        return JsonResponse({
            'name': instance.name,
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


class FloorPlanForm(forms.ModelForm):
    class Meta:
        model = FloorPlan
        exclude = tuple()
        widgets = {'image': ImageWidget()}

    class Media:
        css = {'all': ('django-loci/css/loci.css',)}


class FloorPlanAdmin(TimeReadonlyAdminMixin, admin.ModelAdmin):
    list_display = ['__str__', 'location', 'floor', 'created', 'modified']
    list_select_related = ['location']
    search_fields = ('location__name',)
    raw_id_fields = ('location',)
    save_on_top = True
    form = FloorPlanForm


class UnvalidatedChoiceField(forms.ChoiceField):
    """
    skips ChoiceField validation to allow custom options
    """
    def validate(self, value):
        super(forms.ChoiceField, self).validate(value)


class ObjectLocationForm(forms.ModelForm):
    CHOICES = (
        ('', _('Please select an option')),
        ('new', _('New')),
        ('existing', _('Existing'))
    )
    location_selection = forms.ChoiceField(choices=CHOICES, required=False)
    name = forms.CharField(label=_('Location name'),
                           max_length=75, required=False,
                           help_text=_('Descriptive name of the location '
                                       '(building name, company name, etc.)'))
    address = forms.CharField(max_length=128, required=False)
    geometry = GeometryField(required=False)
    floorplan_selection = forms.ChoiceField(required=False,
                                            choices=CHOICES)
    floorplan = UnvalidatedChoiceField(choices=((None, CHOICES[0][1]),),
                                       required=False)
    floor = forms.IntegerField(required=False)
    image = forms.ImageField(required=False,
                             widget=ImageWidget(thumbnail=False),
                             help_text=_('floor plan image'))
    indoor = forms.CharField(max_length=64, required=False,
                             label=_('indoor position'),
                             widget=FloorPlanWidget)

    class Meta:
        model = ObjectLocation
        exclude = tuple()

    class Media:
        js = ('django-loci/js/loci.js',)
        css = {'all': ('django-loci/css/loci.css',)}

    def __init__(self, *args, **kwargs):
        super(ObjectLocationForm, self).__init__(*args, **kwargs)
        # set initial values for custom fields
        initial = {}
        obj = self.instance
        location = obj.location
        floorplan = obj.floorplan
        if location:
            initial.update({
                'location_selection': 'existing',
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

    def clean_floorplan(self):
        if self.cleaned_data['type'] != 'indoor' or self.cleaned_data['floorplan_selection'] == 'new':
            return None
        pk = self.cleaned_data['floorplan']
        if not pk:
            raise ValidationError(_('Invalid selection'))
        try:
            return FloorPlan.objects.get(pk=pk)
        except FloorPlan.DoesNotExist as e:
            pass
        # TODO maybe here we can call the model validation logic

    def clean(self):
        instance = self.instance
        data = self.cleaned_data
        type_ = data['type']
        msg = _('this field is required for locations of type %(type)s')
        if type_ in ['outdoor', 'indoor'] and not data['location']:
            for field in ['location_selection', 'name', 'address', 'geometry']:
                if field in data and not data[field]:
                    params = {'type': type_}
                    err = ValidationError(msg, params=params)
                    self.add_error(field, err)
        if type_ == 'indoor':
            fields = ['floorplan_selection', 'floor', 'indoor']
            if data.get('floorplan_selection') == 'existing':
                fields.append('floorplan')
            elif data.get('floorplan_selection') == 'new':
                fields.append('image')
            for field in fields:
                if field in data and not data[field]:
                    params = {'type': type_}
                    err = ValidationError(msg, params=params)
                    self.add_error(field, err)
        elif type_ == 'mobile' and not instance.location:
            data['name'] = str(instance.content_object)
            data['address'] = ''
            data['geometry'] = ''
            data['location_selection'] = 'new'
        elif type_ == 'mobile' and instance.location:
            data['location_selection'] = 'existing'
        # clean location
        instance.location = self._get_location_instance()
        instance.location.full_clean()
        # clean floorplan
        if data['type'] == 'indoor':
            instance.floorplan = self._get_floorplan_instance()
            instance.floorplan.full_clean()

    def _get_location_instance(self):
        data = self.cleaned_data
        location = data.get('location') or Location()
        location.name = data.get('name') or location.name
        location.address = data.get('address') or location.address
        location.geometry = data.get('geometry') or location.geometry
        return location

    def _get_floorplan_instance(self):
        data = self.cleaned_data
        instance = self.instance
        floorplan = data.get('floorplan') or FloorPlan()
        floorplan.location = instance.location
        floorplan.floor = data.get('floor') or floorplan.floor
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
        instance.location.save()
        # create or update floorplan
        if data['type'] == 'indoor':
            instance.floorplan = self._get_floorplan_instance()
            instance.floorplan.save()
        # call super
        return super(ObjectLocationForm, self).save(commit=True)


class ObjectLocationInline(TimeReadonlyAdminMixin, GenericStackedInline):
    model = ObjectLocation
    form = ObjectLocationForm
    verbose_name = _('geographic information')
    verbose_name_plural = verbose_name
    raw_id_fields = ('location',)
    max_num = 1
    extra = 1
    template = 'admin/django_loci/location_inline.html'
    fieldsets = (
        (None, {'fields': ('type',)}),
        ('Geographic coordinates', {
            'classes': ('geo', 'coords'),
            'fields': ('location_selection', 'location',
                       'name', 'address', 'geometry'),
        }),
        ('Indoor coordinates', {
            'classes': ('indoor', 'coords'),
            'fields': ('floorplan_selection', 'floorplan',
                       'floor', 'image', 'indoor',),
        })
    )


admin.site.register(Location, LocationAdmin)
admin.site.register(FloorPlan, FloorPlanAdmin)
