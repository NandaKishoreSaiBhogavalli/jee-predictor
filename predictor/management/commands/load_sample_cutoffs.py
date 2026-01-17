import math
import pandas as pd
from django.core.management.base import BaseCommand
from predictor.models import Institute, Cutoff


class Command(BaseCommand):
    help = "Load JOSAA cutoffs from cutoffs_clean.csv into Cutoff table"

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            type=str,
            default="cutoffs_clean.csv",
            help="Path to clean CSV file with cutoffs",
        )
        parser.add_argument(
            "--year",
            type=int,
            default=2025,
            help="Admission year for these cutoffs",
        )

    def handle(self, *args, **options):
        path = options["path"]
        year = options["year"]

        self.stdout.write(self.style.NOTICE(f"Reading CSV: {path} (year={year})"))

        # Load the clean cutoff table
        df = pd.read_csv(path)

        # Normalise column names
        df.columns = [str(c).strip() for c in df.columns]

        # Map CSV columns to our expected names
        # Your CSV should have exactly these headers:
        # Institute, Academic Program Name, Quota, Seat Type, Gender, Opening Rank, Closing Rank
        col_inst = "Institute"
        col_prog = "Academic Program Name"
        col_quota = "Quota"
        col_seat_type = "Seat Type"
        col_gender = "Gender"
        col_open = "Opening Rank"
        col_close = "Closing Rank"

        missing = [
            c
            for c in [
                col_inst,
                col_prog,
                col_quota,
                col_seat_type,
                col_gender,
                col_open,
                col_close,
            ]
            if c not in df.columns
        ]
        if missing:
            self.stdout.write(self.style.ERROR(f"Missing columns in CSV: {missing}"))
            self.stdout.write(self.style.WARNING(f"Available columns: {list(df.columns)}"))
            return

        # Optional: clean up labels a bit (keep strings exactly as in CSV)
        df[col_inst] = df[col_inst].astype(str).str.strip()
        df[col_prog] = df[col_prog].astype(str).str.strip()
        df[col_quota] = df[col_quota].astype(str).str.strip()
        df[col_seat_type] = df[col_seat_type].astype(str).str.strip()
        df[col_gender] = df[col_gender].astype(str).str.strip()

        # Wipe existing data so we reload from clean CSV
        Cutoff.objects.all().delete()

        created, skipped = 0, 0

        for _, row in df.iterrows():
            inst_name = row[col_inst]
            prog_name = row[col_prog]
            quota = row[col_quota]
            seat_type = row[col_seat_type]
            gender = row[col_gender]

            # Skip rows with missing or non‑numeric ranks
            if pd.isna(row[col_open]) or pd.isna(row[col_close]):
                skipped += 1
                continue

            try:
                opening_rank = int(str(row[col_open]).replace("P", ""))
                closing_rank = int(str(row[col_close]).replace("P", ""))
            except (ValueError, TypeError):
                skipped += 1
                continue

            institute, _ = Institute.objects.get_or_create(
                name=inst_name,
                defaults={"state": "", "institute_type": ""},
            )

            Cutoff.objects.create(
                institute=institute,
                program_name=prog_name,
                quota=quota,
                seat_type=seat_type,
                gender=gender,
                year=year,
                opening_rank=opening_rank,
                closing_rank=closing_rank,
            )
            created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created={created}, Skipped={skipped}"
            )
        )
