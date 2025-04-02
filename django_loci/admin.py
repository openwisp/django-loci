from django.contrib import admin

from .base.admin import (
    AbstractFloorPlanAdmin,
    AbstractFloorPlanForm,
    AbstractFloorPlanInline,
    AbstractLocationAdmin,
    AbstractLocationForm,
    AbstractObjectLocationForm,
    AbstractObjectLocationInline,
)
from .models import FloorPlan, Location, ObjectLocation


class FloorPlanForm(AbstractFloorPlanForm):
    class Meta(AbstractFloorPlanForm.Meta):
        model = FloorPlan


class FloorPlanAdmin(AbstractFloorPlanAdmin):
    form = FloorPlanForm


class LocationForm(AbstractLocationForm):
    class Meta(AbstractLocationForm.Meta):
        model = Location


class FloorPlanInline(AbstractFloorPlanInline):
    form = FloorPlanForm
    model = FloorPlan


class LocationAdmin(AbstractLocationAdmin):
    form = LocationForm
    inlines = [FloorPlanInline]

    # kept for backward compatibility with Django 3.2.18
    def _create_formsets(self, request, obj, change):
        # 'data' is not present in POST request for django 3.2.18
        if request.method == 'POST' and not request.POST.get('data', None):
            data = request.POST.copy()
            if data['type'] == 'outdoor':
                data['floorplan_set-TOTAL_FORMS'] = '0'
            request.POST = data
        return super()._create_formsets(request, obj, change)

    # for django >= 4.0
    def get_formset_kwargs(self, request, obj, inline, prefix):
        formset_kwargs = super().get_formset_kwargs(request, obj, inline, prefix)
        # manually set TOTAL_FORMS to 0 if the type is outdoor to avoid floorplan form creation
        if request.method == 'POST' and formset_kwargs['data']['type'] == 'outdoor':
            formset_kwargs['data']['floorplan_set-TOTAL_FORMS'] = '0'
        return formset_kwargs


class ObjectLocationForm(AbstractObjectLocationForm):
    class Meta(AbstractObjectLocationForm.Meta):
        model = ObjectLocation


class ObjectLocationInline(AbstractObjectLocationInline):
    model = ObjectLocation
    form = ObjectLocationForm


admin.site.register(FloorPlan, FloorPlanAdmin)
admin.site.register(Location, LocationAdmin)
