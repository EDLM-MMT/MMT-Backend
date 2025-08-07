from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from academic_institute.models import AcademicInstitute
from generate_transcript.admin import DegreeInline


# Register your models here.
@admin.register(AcademicInstitute)
class AcademicInstituteAdmin(GuardedModelAdmin):
    list_display = ('id', 'institute', 'managed_by_import')
    list_display_links = ['id', 'institute',]
    inlines = [DegreeInline,]
    search_fields = ['institute',]
    list_filter = ['managed_by_import',]
    autocomplete_fields = ['group', 'admins',]

    # fields to display in the admin site
    fieldsets = (
        (
            "General",
            {
                "fields": (
                    "institute", "group", "admins", "managed_by_import"
                )
            },
        ),
    )
