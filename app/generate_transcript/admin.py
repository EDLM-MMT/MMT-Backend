from django.contrib import admin
from generate_transcript.models import (AcademicCourse, AcademicCourseArea,
                                        AcademicInstitute, ACEMapping,
                                        AreasAndHour, Degree, MilitaryCourse,
                                        Transcript)
from guardian.admin import GuardedModelAdmin

# Register your models here.


@admin.register(AcademicCourseArea)
class AcademicCourseAreaAdmin(admin.ModelAdmin):
    list_display = ('id', 'course_area',)


@admin.register(AcademicCourse)
class AcademicCourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'academic_course_area')


@admin.register(AcademicInstitute)
class AcademicInstituteAdmin(admin.ModelAdmin):
    list_display = ('id', 'institute',)


@admin.register(ACEMapping)
class ACEMappingAdmin(admin.ModelAdmin):
    list_display = ('id', 'academic_course_area',)


@admin.register(AreasAndHour)
class AreasAndHourAdmin(admin.ModelAdmin):
    list_display = ('id', 'academic_course_area', 'hours')


@admin.register(Degree)
class DegreeAdmin(admin.ModelAdmin):
    list_display = ('id', 'degree', 'area_and_hours')


@admin.register(MilitaryCourse)
class MilitaryCourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'course_id')

    # fields to display in the admin site
    fieldsets = (
        (
            "Military Course Configuration",
            {
                # on the same line
                "fields": (
                    "course_id",
                )
            },
        ),
        (
            "Users",
            {
                "fields": (
                    "user_id",
                )
            }
        ),
    )
    filter_horizontal = ("user_id",)


@admin.register(Transcript)
class TranscriptAdmin(GuardedModelAdmin):
    list_display = ('id', 'subject')
