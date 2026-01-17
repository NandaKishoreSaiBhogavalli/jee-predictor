from django.urls import path
from . import views


urlpatterns = [
    path("", views.landing, name="landing"),
    path("predict/", views.home, name="home"),
    path("colleges/", views.colleges, name="colleges"),

    # new routes for unlock flow
    path("unlock/", views.start_lead, name="start_lead"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path("reset-unlock/", views.reset_unlock, name="reset_unlock"),
]
