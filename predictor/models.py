from django.db import models


class MarksBand(models.Model):
    min_marks = models.IntegerField()
    max_marks = models.IntegerField()
    percentile = models.FloatField()
    min_rank = models.IntegerField()
    max_rank = models.IntegerField()

    class Meta:
        ordering = ['-min_marks']

    def __str__(self):
        return f"{self.min_marks}-{self.max_marks} marks → {self.percentile}%"


class Institute(models.Model):
    name = models.CharField(max_length=200, unique=True)
    state = models.CharField(max_length=50, blank=True)

    # IIT, NIT, IIIT, GFTI (we keep it flexible but add choices for safety)
    institute_type = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ("IIT", "IIT"),
            ("NIT", "NIT"),
            ("IIIT", "IIIT"),
            ("GFTI", "GFTI"),
        ],
    )

    def __str__(self):
        return self.name


class Cutoff(models.Model):
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE)
    program_name = models.CharField(max_length=255)
    quota = models.CharField(max_length=20)          # AI, HS, OS, etc.
    seat_type = models.CharField(max_length=50)      # OPEN, EWS, OBC-NCL, SC, ST...
    gender = models.CharField(max_length=50)         # Gender-Neutral, Female-only (including Supernumerary)
    opening_rank = models.IntegerField()
    closing_rank = models.IntegerField()
    year = models.IntegerField(default=2025)

    class Meta:
        indexes = [
            models.Index(
                fields=[
                    'year',
                    'institute',
                    'program_name',
                    'quota',
                    'seat_type',
                    'gender',
                ]
            ),
        ]

    def __str__(self):
        return (
            f"{self.institute.name[:30]}... - "
            f"{self.program_name[:40]} "
            f"({self.seat_type}, {self.gender}): "
            f"{self.opening_rank}-{self.closing_rank}"
        )

class Lead(models.Model):
    PASS_YEAR_CHOICES = [
        ("2026", "2026"),
        ("2027", "2027"),
        ("2028", "2028"),
    ]

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)  # store as string
    state = models.CharField(max_length=50)
    pass_year = models.CharField(max_length=4, choices=PASS_YEAR_CHOICES)
    gender = models.CharField(max_length=50)

    # context from predictor
    marks = models.IntegerField(null=True, blank=True)
    approx_rank = models.IntegerField(null=True, blank=True)
    category = models.CharField(max_length=50, blank=True)

    # OTP fields (dummy for now)
    otp_code = models.CharField(max_length=10, blank=True)
    otp_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.phone})"
