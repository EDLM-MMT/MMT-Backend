
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from generate_transcript.models import MilitaryExperience
from users.forms import UserRecordChangeForm, UserRecordForm
from users.models import MOS, MMTUser, UserRecord

# Register your models here.


class MilitaryExperienceInline(admin.TabularInline):
    model = MilitaryExperience.user_id.through
    verbose_name = 'Military Experience'
    verbose_name_plural = 'Military Experience'


@admin.register(MMTUser)
class MMTUserAdmin(UserAdmin):
    model = MMTUser
    search_fields = ('email', 'first_name',)
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    ordering = ('-date_joined', '-last_login')
    list_display = ('email', 'first_name',
                    'is_active', 'is_staff', 'last_login')
    fieldsets = (
        (None,
         {'fields': ('email', 'first_name', 'last_name', 'password',
                     'eso_default', 'position',)}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups',
                                    'user_permissions',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'eso_default',
                       'position', 'password1', 'password2', 'is_active',
                       'is_staff', 'groups', 'user_permissions',)}
         ),
    )
    filter_horizontal = ['groups', 'user_permissions', ]


@admin.register(UserRecord)
class UserRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'first_name', 'last_name', 'rank',
                    'status', 'branch', 'mos')
    inlines = [MilitaryExperienceInline]
    form = UserRecordChangeForm
    add_form = UserRecordForm

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during user creation
        """
        defaults = {}
        if obj is None:
            defaults["form"] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)


@admin.register(MOS)
class MOSAdmin(admin.ModelAdmin):
    list_display = ('code', 'name',)
