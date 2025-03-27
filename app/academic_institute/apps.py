from django.apps import AppConfig


class AcademicInstituteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'academic_institute'

    def ready(self):
        super(AcademicInstituteConfig, self).ready()
        import academic_institute.signals
        academic_institute.signals.create_groups
        academic_institute.signals.update_permissions
        academic_institute.signals.\
            remove_obj_perms_connected_with_academic_institute
