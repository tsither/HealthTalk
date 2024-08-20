from django.apps import AppConfig


class UiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ui'
class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        import users.signals