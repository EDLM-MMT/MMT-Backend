
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from generate_transcript.models import MilitaryCourse
from users.models import MMTUser, UserRecord

# Register your models here.


class MilitaryCourseInline(admin.TabularInline):
    model = MilitaryCourse.user_id.through
    verbose_name = 'Military Course'
    verbose_name_plural = 'Military Courses'


@admin.register(MMTUser)
class XDSUserAdmin(UserAdmin):
    model = MMTUser
    search_fields = ('email', 'first_name',)
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    ordering = ('-date_joined', '-last_login')
    list_display = ('email', 'first_name',
                    'is_active', 'is_staff', 'last_login')
    fieldsets = (
        (None, {'fields': ('email', 'first_name', 'last_name',)}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups',
                                    'user_permissions',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name',
                       'password1', 'password2', 'is_active', 'is_staff',
                       'groups', 'user_permissions',)}
         ),
    )
    filter_horizontal = ['groups', 'user_permissions', ]


@admin.register(UserRecord)
class UserRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'email',)
    inlines = [MilitaryCourseInline]
