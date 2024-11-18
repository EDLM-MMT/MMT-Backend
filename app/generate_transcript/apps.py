from django.apps import AppConfig


class GenerateTranscriptConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'generate_transcript'

    def ready(self):
        super(GenerateTranscriptConfig, self).ready()
        import generate_transcript.signals
        generate_transcript.signals.set_permission
