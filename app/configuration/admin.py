from django.contrib import admin

from .models import MMTConfig

# Register your models here.


@admin.register(MMTConfig)
class MMTConfigAdmin(admin.ModelAdmin):
    list_display = ('elrr_services_api', 'xis_api',)
    list_display_links = ('elrr_services_api', 'xis_api',)

    # fields to display in the admin site
    fieldsets = (
        (
            "ELRR",
            {
                "fields": (
                    "elrr_services_api", "elrr_api_key"
                )
            },
        ),
        (
            "XIS",
            {
                "fields": (
                    "xis_api",
                )
            },
        ),
    )
