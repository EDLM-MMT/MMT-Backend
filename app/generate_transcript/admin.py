from django.contrib import admin
from generate_transcript.models import (AcademicCourse, AcademicCourseArea,
                                        AcademicInstitute, AreasAndHour,
                                        Degree, MilitaryCourse, Transcript)
from guardian.admin import GuardedModelAdmin

# Register your models here.


class DegreeInline(admin.TabularInline):
    model = Degree
    fields = ('degree', 'mos',)
    extra = 3


class AreasAndHourInline(admin.TabularInline):
    model = AreasAndHour
    fields = ('degree', 'academic_course_area', 'hours',)
    extra = 3


@admin.register(AcademicCourseArea)
class AcademicCourseAreaAdmin(admin.ModelAdmin):
    list_display = ('id', 'course_area',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(academiccourse=None)


@admin.register(AcademicCourse)
class AcademicCourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'course_area')


@admin.register(AcademicInstitute)
class AcademicInstituteAdmin(admin.ModelAdmin):
    list_display = ('id', 'institute',)
    inlines = [DegreeInline,]

    # fields to display in the admin site
    fieldsets = (
        (
            "General",
            {
                # on the same line
                "fields": (
                    "institute",
                )
            },
        ),
    )


@admin.register(AreasAndHour)
class AreasAndHourAdmin(admin.ModelAdmin):
    list_display = ('degree', 'academic_course_area', 'hours')

    # fields to display in the admin site
    fieldsets = (
        (
            "General",
            {
                # on the same line
                "fields": (
                    "hours",
                )
            },
        ),
        (
            "Connections",
            {
                # on the same line
                "fields": (
                    "academic_course_area",
                    "degree",
                    "military_course",
                )
            },
        ),
    )


@admin.register(Degree)
class DegreeAdmin(admin.ModelAdmin):
    list_display = ('degree', 'institute')
    list_filter = (('institute', admin.RelatedOnlyFieldListFilter),)
    inlines = [AreasAndHourInline,]

    # fields to display in the admin site
    fieldsets = (
        (
            "General",
            {
                # on the same line
                "fields": (
                    "degree",
                )
            },
        ),
        (
            "Connections",
            {
                "fields": (
                    "institute",
                    "mos",
                )
            }
        ),
    )
    filter_horizontal = ("mos",)


@admin.register(MilitaryCourse)
class MilitaryCourseAdmin(admin.ModelAdmin):
    list_display = ('course_id',)
    inlines = [AreasAndHourInline,]

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
