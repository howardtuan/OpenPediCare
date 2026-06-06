from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Patient, Profile, Visit, VisitOutput
from core.services.ai import mock_generate
from core.services.prompts import PROMPT_VERSION


DOCTOR_EMAIL = "doctor@example.test"
PARENT_EMAIL = "parent@example.test"


class Command(BaseCommand):
    help = "Create public-safe demo users and sample pediatric data."

    def _user_from_email_or_create(self, username, defaults):
        user = User.objects.filter(username=username).first()
        if not user:
            user = User(username=username)
        user.email = defaults["email"]
        user.first_name = defaults.get("first_name", "")
        user.last_name = defaults.get("last_name", "")
        return user

    def handle(self, *args, **options):
        doctor = self._user_from_email_or_create(
            DOCTOR_EMAIL,
            {"email": DOCTOR_EMAIL, "first_name": "demo", "last_name": "doctor"},
        )
        doctor.set_password("Doctor123!")
        doctor.is_staff = True
        doctor.save()
        Profile.objects.update_or_create(
            user=doctor,
            defaults={
                "role": Profile.ROLE_DOCTOR,
                "display_name": "demo doctor",
                "organization": "OpenPediCare Demo Clinic",
                "signature_text": "demo doctor",
            },
        )

        parent = self._user_from_email_or_create(
            PARENT_EMAIL,
            {"email": PARENT_EMAIL, "first_name": "Demo", "last_name": "Parent"},
        )
        parent.set_password("Parent123!")
        parent.save()
        Profile.objects.update_or_create(
            user=parent,
            defaults={"role": Profile.ROLE_PARENT, "display_name": "Demo Parent"},
        )

        patient = Patient.objects.filter(doctor=doctor, name="Demo Child").first()
        if not patient:
            patient = Patient(doctor=doctor, name="Demo Child")
        patient.name = "Demo Child"
        patient.guardian_name = "Demo Parent"
        patient.guardian_email = PARENT_EMAIL
        patient.guardian_phone = "+1-555-0100"
        patient.age_years = 7
        patient.gender = "female"
        patient.weight_kg = "22.50"
        patient.allergies = "No known drug allergies"
        patient.notes = "Public-safe demo patient for fever and follow-up workflow testing."
        patient.save()

        visit = Visit.objects.filter(doctor=doctor, patient=patient).first()
        if not visit:
            visit = Visit.objects.create(
                doctor=doctor,
                patient=patient,
                clinical_scenario=Visit.SCENARIO_FEVER,
                diagnosis="Fever follow-up",
                consent_confirmed=True,
                transcript=(
                    "The caregiver reports fever since yesterday, highest temperature 38.8 C. "
                    "Appetite is slightly lower, activity is acceptable. The physician reviewed hydration, rest, "
                    "breathing observation, and when to seek care."
                ),
                doctor_notes="Use fever medicine only as directed. Seek care for breathing difficulty, lethargy, or fever lasting more than three days.",
                status=Visit.STATUS_REVIEW,
            )
        payload = mock_generate(visit)
        VisitOutput.objects.update_or_create(
            visit=visit,
            defaults={
                "visit_summary": payload["visit_summary"],
                "parent_education": payload["parent_education"],
                "patient_education": payload["patient_education"],
                "parent_summary": payload["visit_summary"],
                "child_explanation": payload["patient_education"],
                "school_note": payload["parent_education"],
                "warning_signs": payload["warning_signs"],
                "follow_up_plan": payload["follow_up_plan"],
                "ai_provider": "demo",
                "ai_model": "",
                "prompt_version": PROMPT_VERSION,
                "generated_at": timezone.now(),
            },
        )

        self.stdout.write(self.style.SUCCESS("Demo data ready: doctor@example.test and parent@example.test."))
