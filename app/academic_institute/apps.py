from django.apps import AppConfig


class AcademicInstituteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'academic_institute'

    def ready(self):
        super(AcademicInstituteConfig, self).ready()
        import academic_institute.signals
