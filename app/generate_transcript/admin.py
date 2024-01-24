from django.contrib import admin

from generate_transcript.models import (AcademicCourse, AcademicCourseArea,
                                        AcademicInstitute, ACEMapping,
                                        AreasAndHour, Degree, MilitaryCourse)

# Register your models here.


@admin.register(AcademicCourseArea)
class AcademicCourseAreaAdmin(admin.ModelAdmin):
    list_display = ('id', 'course_area',)


@admin.register(AcademicCourse)
class AcademicCourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'courses', 'academic_course_areas')


@admin.register(AcademicInstitute)
class AcademicInstituteAdmin(admin.ModelAdmin):
    list_display = ('id', 'institute', 'degree_offered')


@admin.register(ACEMapping)
class ACEMappingAdmin(admin.ModelAdmin):
    list_display = ('id', 'academic_course_areas',)


@admin.register(AreasAndHour)
class AreasAndHourAdmin(admin.ModelAdmin):
    list_display = ('id', 'academic_areas', 'hours')


@admin.register(Degree)
class DegreeAdmin(admin.ModelAdmin):
    list_display = ('id', 'degree', 'areas_and_hours')


@admin.register(MilitaryCourse)
class MilitaryCourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'course')
