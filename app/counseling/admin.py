from counseling.models import CareerPlan, Comment, CoursePlan
from django.contrib import admin
from guardian.admin import GuardedModelAdmin

# Register your models here.


class CommentInline(admin.TabularInline):
    can_delete = False
    model = Comment
    verbose_name = 'Comment'
    verbose_name_plural = 'Comments'
    fields = ('poster', 'comment', 'created',)
    readonly_fields = ('created', 'poster', 'comment',)
    extra = 0


@admin.register(CareerPlan)
class CareerPlanAdmin(GuardedModelAdmin):
    list_display = ('owner', 'eso',)

    inlines = [CommentInline]

    # fields to display in the admin site
    fieldsets = (
        (
            "People",
            {
                # on the same line
                "fields": (
                    "owner",
                    "eso",
                )
            },
        ),
        (
            "Academics",
            {
                "fields": (
                    "degree",
                    "academic_institute",
                    "degree_start_date",
                    "expected_graduation_date",
                )
            }
        ),
    )


@admin.register(Comment)
class CommentAdmin(GuardedModelAdmin):
    list_display = ('poster', 'comment', 'plan')
    readonly_fields = ('created', 'modified',)

    fieldsets = (
        (
            "General",
            {
                # on the same line
                "fields": (
                    "comment",
                )
            },
        ),
        (
            "Connections",
            {
                "fields": (
                    "plan",
                    "poster",
                )
            }
        ),
        (
            "Metadata",
            {
                "fields": (
                    "created",
                )
            }
        ),
    )

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.readonly_fields = (
                'created', 'modified', 'comment', 'poster', 'plan',)
        return super(CommentAdmin, self).get_form(request, obj, **kwargs)


@admin.register(CoursePlan)
class CoursePlanAdmin(GuardedModelAdmin):
    list_display = ('plan', 'course',)

    # fields to display in the admin site
    fieldsets = (
        (
            "General",
            {
                # on the same line
                "fields": (
                    "required",
                    "approved",
                    "expected_semester",
                )
            },
        ),
        (
            "Connections",
            {
                "fields": (
                    "plan",
                    "course",
                )
            }
        ),
    )
