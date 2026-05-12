from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create a couple of default users for local development. Idempotent: safe to run multiple times."

    def handle(self, *args, **options):
        User = get_user_model()

        created = []
        existing = []

        # Admin user: admin / admin
        admin_username = "admin"
        admin_password = "admin"
        admin_email = "admin@example.com"

        admin_user, was_created = User.objects.get_or_create(
            username=admin_username,
            defaults={
                "email": admin_email,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if was_created:
            admin_user.set_password(admin_password)
            admin_user.save(update_fields=["password"])
            created.append(admin_username)
        else:
            existing.append(admin_username)

        # Regular users
        users_spec = [
            ("alice", "alice123", "alice@example.com"),
            ("bob", "bob123", "bob@example.com"),
        ]

        for username, password, email in users_spec:
            user, was_created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                },
            )
            if was_created:
                user.set_password(password)
                user.save(update_fields=["password"])
                created.append(username)
            else:
                existing.append(username)

        # Summary output
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created users: {', '.join(created)}"))
        if existing:
            self.stdout.write(self.style.WARNING(f"Users already existed: {', '.join(existing)}"))
        if not created and not existing:
            self.stdout.write("No user changes were made.")

        self.stdout.write(self.style.SUCCESS("Seeding users complete."))
