from collections import defaultdict

from django.shortcuts import render, redirect
from django.db.models import Q
from .models import MarksBand, Cutoff, Lead
import random
import re  


def user_can_see_all(request):
    return request.session.get("can_see_all_colleges", False)


def reset_unlock(request):
    """
    Dev/helper: clear unlock flag and last prediction
    so masking is active again and predictor starts empty.
    """
    request.session.pop("can_see_all_colleges", None)
    request.session.pop("lead_id", None)
    request.session.pop("last_prediction", None)
    return redirect("home")




def start_lead(request):
    """
    Step 1: collect user details and generate a dummy OTP.
    """
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        state = request.POST.get("state", "").strip()
        pass_year = request.POST.get("pass_year", "").strip()
        terms = request.POST.get("terms", "").strip()  # ✅ NEW: terms checkbox

        # ---- PHONE VALIDATION: 10 digits, starts with 6/7/8/9 ----
        if phone and not re.fullmatch(r'^[6-9]\d{9}$', phone):
            return render(request, "predictor/lead_form.html", {
                "error": "Please enter a valid 10-digit mobile number starting with 6, 7, 8, or 9.",
                "name": name,
                "phone": phone,
                "state": state,
                "pass_year": pass_year,
                "terms": terms,
            })
        # ------------------------------------------------------

        # ✅ REMOVED gender, ADDED terms validation
        if not (name and phone and state and pass_year and terms):
            return render(request, "predictor/lead_form.html", {
                "error": "Please fill all fields including Terms & Conditions.",
                "name": name,
                "phone": phone,
                "state": state,
                "pass_year": pass_year,
                "terms": terms,
            })

        dummy_otp = "123456"  # fixed for now

        lead = Lead.objects.create(
            name=name,
            phone=phone,
            state=state,
            pass_year=pass_year,
            # ✅ gender field removed
            otp_code=dummy_otp,
        )

        request.session["lead_id"] = lead.id

        # remember where user started unlock from
        source = request.GET.get("source") or request.POST.get("source")
        if source in ("predict", "colleges"):
            request.session["unlock_source"] = source
        else:
            request.session.pop("unlock_source", None)

        return redirect("verify_otp")

    # GET: show empty form
    return render(request, "predictor/lead_form.html")




def verify_otp(request):
    """
    Step 2: verify dummy OTP and unlock all colleges.
    """
    lead_id = request.session.get("lead_id")
    lead = Lead.objects.filter(id=lead_id).first()

    if not lead:
        return render(request, "predictor/verify_otp.html", {
            "error": "Session expired. Please fill the form again.",
        })

    if request.method == "POST":
        entered = request.POST.get("otp", "").strip()

        if entered == lead.otp_code:
            lead.otp_verified = True
            lead.save(update_fields=["otp_verified"])
            request.session["can_see_all_colleges"] = True

            # decide where to send user back
            source = request.session.get("unlock_source")

            if source == "colleges":
                # go back to browse colleges; keep same query params in URL
                last_rank = request.session.get("last_colleges_rank", "")
                last_category = request.session.get("last_colleges_category", "OPEN")
                last_gender = request.session.get("last_colleges_gender", "Gender-Neutral")

                return redirect(
                    f"/colleges/?rank={last_rank}&category={last_category}&gender={last_gender}"
                )

            # default: go to predictor
            return redirect("home")
        else:
            return render(request, "predictor/verify_otp.html", {
                "phone": lead.phone,
                "error": "Invalid OTP. Please try again.",
            })

    return render(request, "predictor/verify_otp.html", {
        "phone": lead.phone,
    })


def landing(request):
    return render(request, "predictor/landing.html")


def colleges(request):
    # always start locked when user opens this page directly
    if request.method == "GET" and "rank" not in request.GET:
        # first time visiting /colleges/ in this session: lock view
        request.session.pop("can_see_all_colleges", None)

    rank_str = request.GET.get("rank", "").strip()
    category = request.GET.get("category", "OPEN").strip()
    gender = request.GET.get("gender", "Gender-Neutral").strip()

    context = {
        "rank": rank_str,
        "category": category,
        "gender": gender,
        "cutoffs": None,
    }

    if rank_str.isdigit():
        rank = int(rank_str)
        # remember last browse-colleges search
        request.session["last_colleges_rank"] = rank
        request.session["last_colleges_category"] = category
        request.session["last_colleges_gender"] = gender


        # use AI quota
        quota_filter = ["AI"]

        # STRICT containment: opening_rank <= rank <= closing_rank
        qs = Cutoff.objects.filter(
            year=2025,
            quota__in=quota_filter,
            seat_type=category,
            gender=gender,
            opening_rank__lte=rank,
            closing_rank__gte=rank,
        ).order_by("closing_rank")[:50]

        context["cutoffs"] = qs

        # group by institute name for accordion display
        grouped = defaultdict(list)
        for c in qs:
            grouped[c.institute.name].append(c)

        grouped_items = list(grouped.items())

        if not user_can_see_all(request) and grouped_items:
            grouped_items = [grouped_items[0]]

        context["cutoffs_grouped"] = grouped_items
        context["has_more_institutes"] = len(grouped) > 1
        context["can_see_all"] = user_can_see_all(request)

    return render(request, "predictor/colleges.html", context)


def home(request):
    context = {
        "result": None,
        "error": None,
        "cutoffs": None,
        "category": "OPEN",             # default
        "gender": "Gender-Neutral",     # default
    }

    # --- 1) Handle GET: rebuild last prediction if it exists (used after OTP) ---
    if request.method == "GET":
        saved = request.session.get("last_prediction")
        if saved:
            marks = saved["marks"]
            category = saved["category"]
            gender = saved["gender"]
            min_rank = saved["min_rank"]
            max_rank = saved["max_rank"]

            band = (
                MarksBand.objects
                .filter(min_marks__lte=marks, max_marks__gte=marks)
                .first()
            )

            if band:
                approx_rank = (band.min_rank + band.max_rank) // 2

                context["result"] = {
                    "marks": marks,
                    "percentile": band.percentile,
                    "min_rank": band.min_rank,
                    "max_rank": band.max_rank,
                    "approx_rank": approx_rank,
                }

                context["category"] = category
                context["gender"] = gender

                quota_filter = ["AI"]

                base_qs = Cutoff.objects.filter(
                    year=2025,
                    quota__in=quota_filter,
                    seat_type=category,
                    gender=gender,
                )

                qs = base_qs.filter(
                    opening_rank__lte=max_rank,
                    closing_rank__gte=min_rank,
                ).order_by("closing_rank")[:50]

                context["cutoffs"] = qs

                grouped = defaultdict(list)
                for c in qs:
                    grouped[c.institute.name].append(c)

                grouped_items = list(grouped.items())

                if not user_can_see_all(request) and grouped_items:
                    grouped_items = [grouped_items[0]]

                context["cutoffs_grouped"] = grouped_items
                context["has_more_institutes"] = len(grouped) > 1
                context["can_see_all"] = user_can_see_all(request)

    # --- 2) Handle POST: normal flow when user submits marks form ---
    if request.method == "POST":
        marks_str = request.POST.get("marks", "").strip()
        category = request.POST.get("category", "OPEN").strip()
        gender = request.POST.get("gender", "Gender-Neutral").strip()

        if not marks_str.isdigit():
            context["error"] = "Please enter a valid integer marks."
        else:
            marks = int(marks_str)
            band = (
                MarksBand.objects
                .filter(min_marks__lte=marks, max_marks__gte=marks)
                .first()
            )

            if not band:
                context["error"] = "Marks out of supported range."
            else:
                approx_rank = (band.min_rank + band.max_rank) // 2

                context["result"] = {
                    "marks": marks,
                    "percentile": band.percentile,
                    "min_rank": band.min_rank,
                    "max_rank": band.max_rank,
                    "approx_rank": approx_rank,
                }

                # keep selections for redisplay
                context["category"] = category
                context["gender"] = gender

                # 5% tolerance around approx_rank
                predicted_rank = int(approx_rank)
                tolerance = int(0.05 * predicted_rank)  # 5% window
                min_rank = predicted_rank - tolerance
                max_rank = predicted_rank + tolerance

                # for predictor page we always use AI quota
                quota_filter = ["AI"]

                base_qs = Cutoff.objects.filter(
                    year=2025,
                    quota__in=quota_filter,
                    seat_type=category,
                    gender=gender,
                )

                # any branch whose cutoff band overlaps [min_rank, max_rank]
                qs = base_qs.filter(
                    opening_rank__lte=max_rank,
                    closing_rank__gte=min_rank,
                ).order_by("closing_rank")[:50]

                context["cutoffs"] = qs

                # group by institute name for template
                grouped = defaultdict(list)
                for c in qs:
                    grouped[c.institute.name].append(c)

                grouped_items = list(grouped.items())

                if not user_can_see_all(request) and grouped_items:
                    # show only the first institute group
                    grouped_items = [grouped_items[0]]

                context["cutoffs_grouped"] = grouped_items
                context["has_more_institutes"] = len(grouped) > 1
                context["can_see_all"] = user_can_see_all(request)

                # save this prediction in session so we can restore it after OTP
                request.session["last_prediction"] = {
                    "marks": marks,
                    "category": category,
                    "gender": gender,
                    "min_rank": min_rank,
                    "max_rank": max_rank,
                }

    return render(request, "predictor/home.html", context)
