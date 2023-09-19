from import_export import resources
from .models import LibraryBulkDataLoad

class LibraryBulkDataLoadResource(resources.ModelResource):
    class Meta:
        model = LibraryBulkDataLoad
        exclude = ('id', )
        skip_unchanged = False