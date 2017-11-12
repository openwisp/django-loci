from django.contrib import admin
from django_loci.admin import ObjectLocationInline
from openwisp_utils.admin import TimeReadonlyAdminMixin

from .models import Building


class BuildingAdmin(TimeReadonlyAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'created', 'modified')
    save_on_top = True
    inlines = [ObjectLocationInline]


admin.site.register(Building, BuildingAdmin)
