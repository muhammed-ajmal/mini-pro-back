from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import AlumniDB
class AlumniDBAdmin(ImportExportModelAdmin):
    list_display = ('first_name','last_name','email','contact','batch')

admin.site.register(AlumniDB,AlumniDBAdmin)
