from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User
from quiz.models import Subject


SUBJECTS = [
    ("Математика", "🔢"),
    ("Физика", "⚛️"),
    ("История", "📜"),
    ("Языки", "🌐"),
    ("Программирование", "💻"),
    ("Астрономия", "🔭"),
    ("Психология", "🧠"),
    ("Химия", "🧪"),
    ("Философия", "💡"),
    ("Экономика", "📊"),
]


class Command(BaseCommand):
    help = "Seed default subjects and admin user"

    def handle(self, *args, **options):
        self.stdout.write("Running migrations first...")
        call_command("migrate", "--run-syncdb", verbosity=0)

        # Create default superuser
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(username="admin", password="admin123", email="")
            self.stdout.write(self.style.SUCCESS("  Superuser 'admin' created."))
        else:
            self.stdout.write("  Superuser 'admin' already exists.")

        # Seed subjects
        created = 0
        for name, emoji in SUBJECTS:
            _, was_created = Subject.objects.get_or_create(
                name=name, defaults={"emoji": emoji, "is_active": True}
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"  Created: {emoji} {name}"))
            else:
                self.stdout.write(f"  Exists: {emoji} {name}")

        self.stdout.write(self.style.SUCCESS(f"\n Done. {created} subjects created."))