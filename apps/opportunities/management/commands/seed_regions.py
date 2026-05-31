from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.opportunities.models import Region

MANITOBA_REGIONS = [
    "Winnipeg",
    "Interlake",
    "Pembina Valley",
    "Central Plains",
    "Westman",
    "Parklands",
    "Northern Manitoba",
    "Eastman",
    "Southeast",
]


class Command(BaseCommand):
    help = "Seed Manitoba regions into the database"

    def handle(self, *args, **options):
        created_count = 0
        for region_name in MANITOBA_REGIONS:
            region, created = Region.objects.get_or_create(
                name=region_name,
                defaults={"slug": slugify(region_name)},
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"  Created region: {region_name}")
                )
            else:
                self.stdout.write(f"  Region already exists: {region_name}")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone! Created {created_count} new regions "
                f"({len(MANITOBA_REGIONS)} total)."
            )
        )
