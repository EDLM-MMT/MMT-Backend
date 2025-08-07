from django.apps import AppConfig


class GenerateTranscriptConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'generate_transcript'

    def ready(self):
        super(GenerateTranscriptConfig, self).ready()
        import generate_transcript.signals
        generate_transcript.signals.set_permission
        generate_transcript.signals.create_transcript
        generate_transcript.signals.my_post_save_user_handler
        generate_transcript.signals.my_post_save_group_handler
        generate_transcript.signals.remove_obj_perms_connected_with_transcript
        generate_transcript.signals.\
            remove_obj_perms_connected_with_transcript_status
        generate_transcript.signals.revoke_access
