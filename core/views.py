from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from core.models import Patient, Profile, Visit
from core.services.pdf import build_school_note_pdf


def _is_doctor(user):
    return user.is_authenticated and hasattr(user, "profile") and user.profile.role == Profile.ROLE_DOCTOR


def _is_parent(user):
    return user.is_authenticated and hasattr(user, "profile") and user.profile.role == Profile.ROLE_PARENT


def home(request):
    if _is_doctor(request.user):
        return redirect("doctor_dashboard")
    if _is_parent(request.user):
        return redirect("parent_dashboard")
    return render(request, "home.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if hasattr(user, "profile") and user.profile.role == Profile.ROLE_DOCTOR:
                return redirect("doctor_dashboard")
            if hasattr(user, "profile") and user.profile.role == Profile.ROLE_PARENT:
                return redirect("parent_dashboard")
            return redirect("home")
        messages.error(request, "帳號或密碼錯誤，請再試一次。")
    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
def doctor_dashboard(request):
    if not _is_doctor(request.user):
        return HttpResponseForbidden("需要醫師權限")
    patients = Patient.objects.filter(doctor=request.user)
    visits = Visit.objects.filter(doctor=request.user).select_related("patient", "output")[:12]
    return render(
        request,
        "doctor_dashboard.html",
        {
            "patients": patients,
            "visits": visits,
            "scenario_choices": Visit.SCENARIO_CHOICES,
            "comic_generation_enabled": settings.COMIC_GENERATION_ENABLED,
        },
    )


@login_required
def doctor_visit_detail(request, visit_id):
    if not _is_doctor(request.user):
        return HttpResponseForbidden("需要醫師權限")
    visit = get_object_or_404(
        Visit.objects.select_related("patient", "doctor").prefetch_related("chunks"),
        id=visit_id,
        doctor=request.user,
    )
    return render(
        request,
        "visit_detail.html",
        {"visit": visit, "comic_generation_enabled": settings.COMIC_GENERATION_ENABLED},
    )


@login_required
def parent_dashboard(request):
    if not _is_parent(request.user):
        return HttpResponseForbidden("Parent access required")
    visits = (
        Visit.objects.filter(patient__guardian_email=request.user.email, output__isnull=False)
        .select_related("patient", "doctor", "output")
        .order_by("-created_at")[:20]
    )
    return render(request, "parent_dashboard.html", {"visits": visits})


def parent_portal(request, token):
    visit = get_object_or_404(
        Visit.objects.select_related("patient", "doctor").filter(share_token=token)
    )
    if not hasattr(visit, "output"):
        raise Http404("文件尚未產生")
    return render(request, "parent_portal.html", {"visit": visit})


def portal_school_pdf(request, token):
    visit = get_object_or_404(Visit.objects.select_related("patient", "doctor"), share_token=token)
    if not hasattr(visit, "output"):
        raise Http404("文件尚未產生")
    pdf = build_school_note_pdf(visit)
    return FileResponse(
        pdf,
        as_attachment=True,
        filename=f"openpedicare-school-note-{visit.id}.pdf",
        content_type="application/pdf",
    )


def demo_redirect(request):
    messages.info(request, "Demo accounts are ready: doctor@example.test / Doctor123! and parent@example.test / Parent123!")
    return redirect(reverse("login"))
