from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from generate_transcript.models import (AcademicCourse, AcademicCourseArea,
                                        AreasAndHour, Degree, MilitaryCourse,
                                        MilitaryCourse_User,
                                        MilitaryExperience, MilitaryTestResult,
                                        Transcript, TranscriptStatus)

# Register your models here.


class DegreeInline(admin.TabularInline):
    model = Degree
    fields = ('degree', 'mos',)
    extra = 3


class AreasAndHourInline(admin.TabularInline):
    model = AreasAndHour
    fields = ('degree', 'academic_course_area', 'hours', 'level')
    extra = 3


@admin.register(AcademicCourseArea)
class AcademicCourseAreaAdmin(admin.ModelAdmin):
    list_display = ('id', 'course_area', )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(academiccourse=None)


@admin.register(AcademicCourse)
class AcademicCourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'course_area')


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
                    "hours", "level"
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


@admin.register(MilitaryExperience)
class MilitaryExperienceAdmin(admin.ModelAdmin):
    list_display = ('id', 'experience_id',)
    inlines = [AreasAndHourInline,]

    filter_horizontal = ("user_id",)


@admin.register(MilitaryCourse)
class MilitaryCourseAdmin(admin.ModelAdmin):
    list_display = ('experience_id', 'course_name')
    inlines = [AreasAndHourInline,]

    # fields to display in the admin site
    fieldsets = (
        (
            "Military Course Configuration",
            {
                # on the same line
                "fields": (
                    "experience_id",
                    "course_name",
                    "ACE_identifier",
                )
            },
        ),
        # (
        #     "Users",
        #     {
        #         "fields": (
        #             "user_id",
        #         )
        #     }
        # ),
    )
    filter_horizontal = ("user_id",)


@admin.register(MilitaryTestResult)
class MilitaryTestResultAdmin(MilitaryCourseAdmin):
    list_display = ('course_name', 'test_type',)
    search_fields = ('course_name',)
    list_filter = ('test_type',)
    fieldsets = (
        (
            "Military Test Result",
            {
                "fields": (
                    "experience_id",
                    "course_name",
                    "test_type",
                    "hours",
                    "passing",
                )
            },
        ),
    )


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
