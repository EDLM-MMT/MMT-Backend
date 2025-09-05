from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        super(UsersConfig, self).ready()
        import users.signals
        users.signals.create_transcript  # pylint: disable=pointless-statement
