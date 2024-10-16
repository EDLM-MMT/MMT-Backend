from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from inquiry.models import Inquiry, InquiryComment, InquiryFAQ

# Register your models here.


class CommentInline(admin.TabularInline):
    can_delete = False
    model = InquiryComment
    verbose_name = 'Comment'
    verbose_name_plural = 'Comments'
    fields = ('poster', 'comment', 'created',)
    readonly_fields = ('created', 'poster', 'comment',)
    extra = 0


@admin.register(InquiryComment)
class CommentAdmin(GuardedModelAdmin):
    list_display = ('poster', 'comment', 'inquiry')
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
                    "inquiry",
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
                'created', 'modified', 'comment', 'poster', 'inquiry',)
        return super(CommentAdmin, self).get_form(request, obj, **kwargs)


@admin.register(Inquiry)
class InquiryAdmin(GuardedModelAdmin):
    list_display = ('owner', 'assigned', 'default_assigned')

    inlines = [CommentInline]

    # fields to display in the admin site
    fieldsets = (
        (
            "People",
            {
                # on the same line
                "fields": (
                    "owner",
                    "email",
                    "name",
                    "assigned",
                )
            },
        ),
        (
            "Inquiry",
            {
                "fields": (
                    "description",
                    "subject",
                    "inquiry_type",
                    "file",
                )
            }
        ),
    )


@admin.register(InquiryFAQ)
class InquiryFAQAdmin(GuardedModelAdmin):
    list_display = ('issue', 'default_assigned')

    # inlines = [CommentInline]

    # fields to display in the admin site
    fieldsets = (
        (
            "Details",
            {
                # on the same line
                "fields": (
                    "issue",
                    "response",
                    "default_assigned",
                    "status"
                )
            },
        ),
    )
