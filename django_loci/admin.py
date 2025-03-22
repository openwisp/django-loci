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
