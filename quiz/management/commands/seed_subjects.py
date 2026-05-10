from django.core.management.base import BaseCommand
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
    help = "Seed default subjects"

    def handle(self, *args, **options):
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

        self.stdout.write(self.style.SUCCESS(f"\n✅ Done. {created} subjects created."))
