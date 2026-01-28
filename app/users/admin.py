
from urllib.parse import quote as urlquote

from django.contrib import admin
from django.contrib.admin.utils import quote
from django.contrib.auth.admin import UserAdmin
from django.db.models import Q
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from guardian.shortcuts import get_objects_for_user

from generate_transcript.models import MilitaryExperience
from users.forms import UserRecordChangeForm, UserRecordForm
from users.models import MOS, MMTUser, UserRecord

# Register your models here.


class MilitaryExperienceInline(admin.TabularInline):
    model = MilitaryExperience.user_id.through
    verbose_name = 'Military Experience'
    verbose_name_plural = 'Military Experience'
    raw_id_fields = ['course_id',]


class DANTESAdminGroupFilter(admin.SimpleListFilter):
    title = "is DANTES admin"
    parameter_name = "dantes"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return [
            ("1", "Yes"),
            ("0", "No"),
        ]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() == "1":
            return queryset.filter(groups__name__exact="DANTES ADMIN")
        if self.value() == "0":
            return queryset.exclude(groups__name__exact="DANTES ADMIN")
        return queryset


class AIGroupFilter(admin.SimpleListFilter):
    title = "is Academic Institute user"
    parameter_name = "ai"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return [
            ("1", "Yes"),
            ("0", "No"),
        ]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() == "1":
            return queryset.filter(Q(groups__academic_institutes__isnull=False) | Q(groups__managing__isnull=False)).distinct()
        if self.value() == "0":
            return queryset.exclude(Q(groups__academic_institutes__isnull=False) | Q(groups__managing__isnull=False)).distinct()
        return queryset


@admin.register(MMTUser)
class MMTUserAdmin(UserAdmin):
    model = MMTUser
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_active', 'is_staff',
                   'is_superuser', DANTESAdminGroupFilter,
                   AIGroupFilter, 'user_record__branch', 'last_login')
    ordering = ('-date_joined', '-last_login')
    list_display = ('email', 'first_name', 'last_name', 'last_login',)
    readonly_fields = ('date_joined', 'last_login', 'allowed_transcripts')
    fieldsets = (
        (None,
         {'fields': ('email', 'first_name', 'last_name', 'password',
                     'eso_default', 'position',)}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups',
                                    'user_permissions', 'allowed_transcripts'),
                         "classes": ["collapse"]}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')})
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

    @admin.display(description="Accessible Transcripts")
    def allowed_transcripts(self, instance):
        """
        Retrieve list of transcripts the selected user has access to
        """
        return format_html_join(
            mark_safe("<br>"),
            "{}",
            ((format_html(
                '<a href="{}">{}</a>',
                urlquote(reverse(
                    "admin:users_userrecord_change",
                    args=(quote(transcript.subject.pk),),
                    current_app=self.admin_site.name,
                )),
                str(transcript.subject)),
              ) for transcript in get_objects_for_user(
                instance, "generate_transcript.view_transcript",
                with_superuser=False))
        )


@admin.register(UserRecord)
class UserRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'first_name', 'last_name', 'rank',
                    'status', 'branch', 'mos')
    inlines = [MilitaryExperienceInline]
    form = UserRecordChangeForm
    add_form = UserRecordForm
    raw_id_fields = ['user_profile',]

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during user creation
        """
        defaults = {}
        if obj is None:
            defaults["form"] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)

    def get_queryset(self, request):
        """
        Add filter based on permissions
        """
        from_super = super().get_queryset(request)
        # if have general override (or super user) don't filter
        if request.user.has_perm('users.view_user_record_override'):
            return from_super
        # if has service override filter based on service
        if request.user.has_perm('users.view_service_user_record_override'):
            if hasattr(request.user, 'user_record') and request.user.user_record.branch:
                return from_super.filter(branch=request.user.user_record.branch)
        # otherwise return nothing
        return from_super.none()

    def has_module_permission(self, request):
        """
        Limit access to module
        """
        return request.user.has_perm('users.view_user_record_override') or\
            request.user.has_perm('users.view_service_user_record_override')


@admin.register(MOS)
class MOSAdmin(admin.ModelAdmin):
    list_display = ('code', 'name',)
