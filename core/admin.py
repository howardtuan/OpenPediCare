from django.contrib import admin

from .models import Patient, Profile, TranscriptChunk, Visit, VisitOutput


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "display_name", "organization")
    list_filter = ("role",)
    search_fields = ("user__username", "display_name", "organization")


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("name", "gender", "guardian_name", "age_years", "weight_kg", "doctor", "updated_at")
    list_filter = ("gender", "primary_language")
    search_fields = ("name", "guardian_name", "guardian_email", "guardian_phone")


class VisitOutputInline(admin.StackedInline):
    model = VisitOutput
    extra = 0


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ("patient", "clinical_scenario", "diagnosis", "status", "doctor", "created_at")
    list_filter = ("status", "clinical_scenario")
    search_fields = ("patient__name", "diagnosis", "transcript", "doctor_notes")
    readonly_fields = ("share_token", "audio_delete_after", "created_at", "updated_at")
    inlines = [VisitOutputInline]


@admin.register(TranscriptChunk)
class TranscriptChunkAdmin(admin.ModelAdmin):
    list_display = ("visit", "sequence", "source", "expires_at", "created_at")
    list_filter = ("source",)
