from counseling.models import CareerPlan, Comment, CoursePlan, ESONote
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


class NoteInline(admin.TabularInline):
    can_delete = False
    model = ESONote
    verbose_name = 'ESO Note'
    verbose_name_plural = 'ESO Notes'
    fields = ('purpose', 'poster', 'note', 'created',)
    readonly_fields = ('created', 'poster', 'purpose', 'note',)
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


@admin.register(ESONote)
class ESONoteAdmin(GuardedModelAdmin):
    list_display = ('poster', 'purpose', 'note', 'plan')
    readonly_fields = ('created', 'modified',)

    fieldsets = (
        (
            "General",
            {
                # on the same line
                "fields": (
                    "purpose",
                    "note",
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
                'created', 'modified', 'note', 'poster', 'plan', 'purpose')
        return super(ESONoteAdmin, self).get_form(request, obj, **kwargs)


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
