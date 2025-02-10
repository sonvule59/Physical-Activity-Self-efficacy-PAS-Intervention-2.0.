from django.apps import AppConfig

class TestpasConfig(AppConfig):
    name = 'testpas'

    def ready(self):
        import testpas.signals