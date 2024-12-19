from django.core.management.base import BaseCommand
from django.utils import timezone
from testpas.views import check_code_entries

class Command(BaseCommand):
    help = 'Check for participants who haven\'t entered their code by Day 20'

    def handle(self, *args, **options):
        check_code_entries()