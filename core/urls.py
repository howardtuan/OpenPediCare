from django.urls import path
from django.views.generic.base import RedirectView

from . import api, views


urlpatterns = [
    path("", views.home, name="home"),
    path("favicon.ico", RedirectView.as_view(url="/static/favicon.svg?v=20260606-pink", permanent=False)),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("demo/", views.demo_redirect, name="demo"),
    path("doctor/", views.doctor_dashboard, name="doctor_dashboard"),
    path("doctor/visits/<int:visit_id>/", views.doctor_visit_detail, name="doctor_visit_detail"),
    path("parent/", views.parent_dashboard, name="parent_dashboard"),
    path("portal/<str:token>/", views.parent_portal, name="parent_portal"),
    path("portal/<str:token>/school-note.pdf", views.portal_school_pdf, name="portal_school_pdf"),
    path("api/auth/login", api.login_api, name="api_login"),
    path("api/patient", api.patient_collection, name="api_patient_collection"),
    path("api/visit/start", api.visit_start, name="api_visit_start"),
    path("api/visit/transcribe", api.visit_transcribe, name="api_visit_transcribe"),
    path("api/visit/complete", api.visit_complete, name="api_visit_complete"),
    path("api/output/<int:visit_id>", api.output_detail, name="api_output_detail"),
    path("api/output/<int:visit_id>/approve", api.output_approve, name="api_output_approve"),
    path("api/output/<int:visit_id>/comic", api.output_comic, name="api_output_comic"),
    path("api/output/<int:visit_id>/school-note", api.school_note_pdf, name="api_school_note_pdf"),
]
