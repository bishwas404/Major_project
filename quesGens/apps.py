from django.apps import AppConfig


class QuesgensConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'quesGens'

    def ready(self):
     import quesGens.signals
