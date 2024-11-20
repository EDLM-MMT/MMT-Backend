from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from academic_institute.models import AcademicInstitute
from generate_transcript.admin import DegreeInline


# Register your models here.
@admin.register(AcademicInstitute)
class AcademicInstituteAdmin(GuardedModelAdmin):
    list_display = ('id', 'institute',)
    inlines = [DegreeInline,]

    # fields to display in the admin site
    fieldsets = (
        (
            "General",
            {
                # on the same line
                "fields": (
                    "institute", "group", "admins"
                )
            },
        ),
    )
