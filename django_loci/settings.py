from django.conf import settings

FLOORPLAN_UPLOAD_DIR = getattr(settings, 'LOCI_FLOORPLAN_UPLOAD_DIR', 'floorplans')
