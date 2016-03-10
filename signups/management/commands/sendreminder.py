from django.core.management.base import BaseCommand, CommandError
import signups.emails as emails

class Command(BaseCommand):
    help = 'This command sends reminder emails'
    
    def handle(self, *args, **options):
        emails.sendReminder()