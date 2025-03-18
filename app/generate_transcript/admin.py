from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from generate_transcript.models import (ACEIdentifier, AcademicCourse,
                                        AcademicCourseArea,
                                        AreasAndHour, Degree,
                                        MilitaryCourse,
                                        MilitaryCourse_User,
                                        MilitaryExperience,
                                        Transcript,
                                        TranscriptStatus)

# Register your models here.


class DegreeInline(admin.TabularInline):
    model = Degree
    fields = ('degree', 'mos',)
    extra = 3


class AreasAndHourInline(admin.TabularInline):
    model = AreasAndHour
    fields = ('degree', 'academic_course_area', 'ace_identifier',
              'hours', 'level')
    extra = 3


@admin.register(AcademicCourseArea)
class AcademicCourseAreaAdmin(admin.ModelAdmin):
    list_display = ('id', 'course_area', )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(academiccourse=None)


@admin.register(ACEIdentifier)
class ACEIdentifierAdmin(admin.ModelAdmin):
    list_display = ('id', 'ace_identifier', )
    search_fields = ['ace_identifier',]


@admin.register(AcademicCourse)
class AcademicCourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'course_area')


@admin.register(AreasAndHour)
class AreasAndHourAdmin(admin.ModelAdmin):
    list_display = ('academic_course_area', 'ace_identifier',
                    'military_course', 'hours', 'level')
    search_fields = ['academic_course_area__course_area',
                     'ace_identifier__ace_identifier']
    list_filter = ['ace_identifier__ace_identifier',]

    # fields to display in the admin site
    fieldsets = (
        (
            "General",
            {
                # on the same line
                "fields": (
                    "hours", "level", "version"
                )
            },
        ),
        (
            "Connections",
            {
                # on the same line
                "fields": (
                    "ace_identifier",
                    "academic_course_area",
                    "degree",
                    "military_course",
                )
            },
        ),
        (
            "Dates",
            {
                # on the same line
                "fields": (
                    "start_date",
                    "end_date",
                    "last_updated_on",
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


@admin.register(MilitaryExperience)
class MilitaryExperienceAdmin(admin.ModelAdmin):
    list_display = ('id', 'experience_id',
                    'experience_name', 'rank')
    inlines = [AreasAndHourInline,]

    filter_horizontal = ("user_id",)


@admin.register(MilitaryCourse)
class MilitaryCourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'experience_id', 'experience_name')
    inlines = [AreasAndHourInline,]

    # fields to display in the admin site
    fieldsets = (
        (
            "Military Course Configuration",
            {
                # on the same line
                "fields": (
                    "experience_id",
                )
            },
        ),
    )
    filter_horizontal = ("user_id",)


@admin.register(Transcript)
class TranscriptAdmin(GuardedModelAdmin):
    list_display = ('subject', )
    fields = ['subject', ]

    # def has_module_permission(self, request):
    #     if super().has_module_permission(request):
    #         return True
    #     return self.get_model_objects(request).exists()

    # def get_queryset(self, request):
    #     if request.user.is_superuser:
    #         return super().get_queryset(request)
    #     data = self.get_model_objects(request)
    #     return data

    # def get_model_objects(self, request, action=None, klass=None):
    #     opts = self.opts
    #     actions = [action] if action else ['view', 'change', 'delete']
    #     klass = klass if klass else opts.model
    #     model_name = klass._meta.model_name
    #     return get_objects_for_user(user=request.user,
    #                                 perms=[f'{perm}_{model_name}'
    # for perm in actions],
    #                                 klass=klass, any_perm=True)

    # def has_permission(self, request, obj, action):
    #     opts = self.opts
    #     code_name = f'{action}_{opts.model_name}'
    #     if obj:
    #         return request.
    # user.has_perm(f'{opts.app_label}.{code_name}', obj)
    #     else:
    #         return self.get_model_objects(request).exists()

    # def has_add_permission(self, request, obj=None):
    #      return self.has_permission(request, obj, 'add')

    # def has_change_permission(self, request, obj=None):
    #      return self.has_permission(request, obj, 'change')

    # # def has_delete_permission(self, request, obj=None):
    # #       return self.has_permission(request, obj, 'delete')

    # def has_view_permission(self, request, obj=None):
    #     return self.has_permission(request, obj, 'view')


@admin.register(TranscriptStatus)
class TranscriptStatusAdmin(GuardedModelAdmin):
    list_display = ('transcript', 'recipient', 'academic_institute', 'status')


@admin.register(MilitaryCourse_User)
class MilitaryCourse_UserAdmin(GuardedModelAdmin):
    list_display = ('start_date', 'end_date')
