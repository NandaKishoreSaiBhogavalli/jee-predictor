from django.contrib import admin
from .models import MarksBand, Institute, Cutoff, Lead

@admin.register(MarksBand)
class MarksBandAdmin(admin.ModelAdmin):
    list_display = ('min_marks', 'max_marks', 'percentile', 'min_rank', 'max_rank')
    ordering = ('-min_marks',)

@admin.register(Institute)
class InstituteAdmin(admin.ModelAdmin):
    list_display = ('name', 'state', 'institute_type')
    search_fields = ('name', 'state', 'institute_type')

@admin.register(Cutoff)
class CutoffAdmin(admin.ModelAdmin):
    list_display = ('institute', 'program_name', 'quota', 'seat_type', 'gender', 'opening_rank', 'closing_rank', 'year')
    list_filter = ('year', 'quota', 'seat_type', 'gender')
    search_fields = ('institute__name', 'program_name')


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "state", "pass_year", "gender",
                    "marks", "approx_rank", "category", "otp_verified", "created_at")
    list_filter = ("state", "pass_year", "gender", "otp_verified", "created_at")
    search_fields = ("name", "phone")
