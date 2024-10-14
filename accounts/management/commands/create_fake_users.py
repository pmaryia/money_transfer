import os
from decimal import Decimal

from django.core.management.base import BaseCommand

from faker import Faker

from accounts.constants import ZERO_DECIMAL
from accounts.models import User


DEFAULT_USERS_COUNT = 5
DEFAULT_SUPERUSER_TIN = "1234567890"
DEFAULT_SUPERUSER_PASSWORD = "admin"


def create_fake_users(users_count: int):
    fake = Faker()

    for _ in range(users_count):
        first_name = fake.first_name()
        last_name = fake.last_name()
        tin = fake.unique.numerify(text="##########")
        balance = Decimal(fake.random_number(digits=5)) / 100

        user = User(
            username=tin,
            first_name=first_name,
            last_name=last_name,
            tin=tin,
            balance=balance,
            is_staff=False,
            is_superuser=False,
        )
        user.set_password(tin)
        user.save()


def create_superuser():
    tin = os.getenv("SUPERUSER_TIN", DEFAULT_SUPERUSER_TIN)
    user = User(
        username=tin,
        first_name="admin",
        last_name="admin",
        tin=tin,
        balance=ZERO_DECIMAL,
        is_staff=True,
        is_superuser=True,
    )
    user.set_password(os.getenv("SUPERUSER_PASSWORD", DEFAULT_SUPERUSER_PASSWORD))
    user.save()


class Command(BaseCommand):
    help = "Create fake data for User model"

    def add_arguments(self, parser):
        parser.add_argument(
            "--users_count",
            type=int,
            default=DEFAULT_USERS_COUNT,
            choices=range(1, 101),
            help="Number of fake users to create",
        )

    def handle(self, *args, **options):
        if User.objects.exists():
            self.stdout.write(
                self.style.WARNING("Users already exist. No new users created.")
            )
            return

        users_count = options["users_count"]
        create_fake_users(users_count - 1)  # one user will be superuser
        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {users_count - 1} fake users")
        )

        create_superuser()
        self.stdout.write(self.style.SUCCESS("Successfully created superuser"))
