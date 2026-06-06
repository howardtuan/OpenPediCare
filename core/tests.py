import json

from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings

from core.models import Patient, Profile, Visit


class OpenPediCareFlowTests(TestCase):
    def setUp(self):
        self.doctor = User.objects.create_user(
            username="doctor@example.com",
            email="doctor@example.com",
            password="Doctor123!",
        )
        Profile.objects.create(
            user=self.doctor,
            role=Profile.ROLE_DOCTOR,
            display_name="測試醫師",
            signature_text="測試醫師 MD",
        )
        self.client = Client()

    def post_json(self, url, payload, token=None):
        headers = {}
        if token:
            headers["HTTP_AUTHORIZATION"] = f"Bearer {token}"
        return self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
            **headers,
        )

    @override_settings(IKUNCODE_API_KEY="", OPENAI_API_KEY="")
    def test_jwt_doctor_visit_output_pdf_flow(self):
        login_response = self.post_json(
            "/api/auth/login",
            {"username": "doctor@example.com", "password": "Doctor123!"},
        )
        self.assertEqual(login_response.status_code, 200)
        token = login_response.json()["access_token"]

        patient_response = self.post_json(
            "/api/patient",
            {
                "name": "Demo Patient",
                "age_years": 8,
                "gender": "male",
            },
            token,
        )
        self.assertEqual(patient_response.status_code, 201)
        patient_id = patient_response.json()["patient"]["id"]

        start_response = self.post_json(
            "/api/visit/start",
            {
                "patient_id": patient_id,
            },
            token,
        )
        self.assertEqual(start_response.status_code, 201)
        visit_id = start_response.json()["session_id"]

        complete_response = self.post_json(
            "/api/visit/complete",
            {
                "visit_id": visit_id,
                "transcript": "昨天發燒，活動力尚可，醫師提醒補水與觀察警示徵兆。",
                "doctor_notes": "若呼吸急促或嗜睡需急診。",
            },
            token,
        )
        self.assertEqual(complete_response.status_code, 200)
        output = complete_response.json()["output"]
        self.assertIn("visit_summary", output)
        self.assertIn("parent_education", output)
        self.assertIn("patient_education", output)

        approve_response = self.post_json(f"/api/output/{visit_id}/approve", {}, token)
        self.assertEqual(approve_response.status_code, 200)
        self.assertEqual(approve_response.json()["output"]["status"], Visit.STATUS_APPROVED)

        pdf_response = self.client.get(
            f"/api/output/{visit_id}/school-note",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEqual(pdf_response.status_code, 200)
        self.assertEqual(pdf_response["Content-Type"], "application/pdf")

    def test_session_dashboard_renders(self):
        self.client.login(username="doctor@example.com", password="Doctor123!")
        Patient.objects.create(doctor=self.doctor, name="Demo Child", age_years=7, gender="female")
        response = self.client.get("/doctor/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Realtime pediatric visit")
