from django.conf import settings
from django.utils.module_loading import import_string

DefaultFileStorageClass = import_string(getattr(settings, 'DEFAULT_FILE_STORAGE'))


class OverwriteMixin:
    floorplan_upload_dir = "floorplans"

    @classmethod
    def upload_to(cls, instance, filename):
        """
        passed to FloorPlan.image.upload_to
        """
        ext = filename.split(".")[-1]
        dir_ = cls.floorplan_upload_dir
        return "{0}/{1}.{2}".format(dir_, instance.id, ext)

    def get_available_name(self, name, max_length=None):
        """
        removes file if it already exists
        """
        if self.exists(name):
            self.delete(name)
        return name


class OverwriteStorage(OverwriteMixin, DefaultFileStorageClass):
    """
    Adds the overwrite functionality to the file storage class
    currently in-use by the Django project.
    """

    pass
