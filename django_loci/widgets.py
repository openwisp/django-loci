from django import forms
from django.templatetags.static import static
from leaflet.forms.widgets import LeafletWidget as BaseLeafletWidget

_floorplan_css = {'all': (static('django-loci/css/floorplan-widget.css'),)}


class ImageWidget(forms.FileInput):
    """
    Image widget which can show a thumbnail
    and carries information regarding
    the image width and height
    """
    template_name = 'admin/widgets/image.html'

    def __init__(self, *args, **kwargs):
        self.thumbnail = kwargs.pop('thumbnail', True)
        super(ImageWidget, self).__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        c = super(ImageWidget, self).get_context(name, value, attrs)
        if value and hasattr(value, 'url'):
            c.update({
                'filename': value.name,
                'url': value.url,
                'thumbnail': self.thumbnail,
                'width': value.width,
                'height': value.height,
            })
        return c

    @property
    def media(self):
        css = _floorplan_css
        return forms.Media(css=css)


class FloorPlanWidget(forms.TextInput):
    """
    widget that allows to manage indoor coordinates
    """
    template_name = 'admin/widgets/floorplan.html'

    @property
    def media(self):
        js = (static('django-loci/js/floorplan-widget.js'),)
        css = _floorplan_css
        return forms.Media(js=js, css=css)


class LeafletWidget(BaseLeafletWidget):
    include_media = True
    geom_type = 'GEOMETRY'
    template_name = 'leaflet/admin/widget.html'
    modifiable = True
    map_width = '100%'
    map_height = '400px'
    display_raw = False
    settings_overrides = {}
