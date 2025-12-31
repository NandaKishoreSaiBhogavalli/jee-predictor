from django.core.management.base import BaseCommand
from predictor.models import Institute


class Command(BaseCommand):
    help = "Classify institutes into IIT / NIT / IIIT / GFTI based on their names"

    def handle(self, *args, **options):
        updated = 0

        for inst in Institute.objects.all():
            n = inst.name.upper()

            if "INDIAN INSTITUTE OF TECHNOLOGY" in n:
                new_type = "IIT"
            elif "NATIONAL INSTITUTE OF TECHNOLOGY" in n:
                new_type = "NIT"
            elif "INSTITUTE OF INFORMATION TECHNOLOGY" in n or "IIIT" in n:
                new_type = "IIIT"
            else:
                new_type = "GFTI"

            if inst.institute_type != new_type:
                inst.institute_type = new_type
                inst.save()
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"Updated {updated} institutes."))
