from django.core.management.base import BaseCommand
from users.models import User

class Command(BaseCommand):
    help = 'Deletes all user accounts from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--keep-superuser',
            action='store_true',
            help='Keep superuser accounts',
        )

    def handle(self, *args, **options):
        keep_superuser = options['keep_superuser']
        
        if keep_superuser:
            users = User.objects.filter(is_superuser=False)
            count = users.count()
            users.delete()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deleted {count} non-superuser accounts')
            )
        else:
            count = User.objects.count()
            User.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deleted all {count} user accounts')
            ) 