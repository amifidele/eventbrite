from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_arguments(
            'file_name', type=str, help='the txt file that contain event details'
        )
    def handle(self, *args, **kwargs):
        file_name = kwargs['file_name']
        