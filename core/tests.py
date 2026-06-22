import base64
import hashlib
import hmac
import json

from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings

from core.models import LineParentLink, Patient, Profile, Visit, VisitOutput


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

    def post_signed_line_webhook(self, payload, secret="line-test-secret", signature=None):
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        if signature is None:
            digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).digest()
            signature = base64.b64encode(digest).decode("utf-8")
        return self.client.post(
            "/linebot/webhook",
            data=body,
            content_type="application/json",
            HTTP_X_LINE_SIGNATURE=signature,
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

    @override_settings(
        DEBUG=True,
        LINE_CHANNEL_SECRET="line-test-secret",
        LINE_CHANNEL_ACCESS_TOKEN="",
        LINEBOT_REQUIRE_SIGNATURE=True,
    )
    def test_linebot_accepts_verified_empty_webhook(self):
        response = self.post_signed_line_webhook({"destination": "Udemo", "events": []})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["events"], 0)

    @override_settings(
        LINE_CHANNEL_SECRET="line-test-secret",
        LINE_CHANNEL_ACCESS_TOKEN="",
        LINEBOT_REQUIRE_SIGNATURE=True,
    )
    def test_linebot_rejects_invalid_signature(self):
        response = self.post_signed_line_webhook({"destination": "Udemo", "events": []}, signature="bad")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "invalid_line_signature")

    @override_settings(
        DEBUG=True,
        LINE_CHANNEL_SECRET="line-test-secret",
        LINE_CHANNEL_ACCESS_TOKEN="",
        LINEBOT_PUBLIC_BASE_URL="https://clinic.example.test",
        LINEBOT_REQUIRE_SIGNATURE=True,
        LINEBOT_ONLY_APPROVED_VISITS=False,
    )
    def test_linebot_returns_recent_parent_visit_record(self):
        patient = Patient.objects.create(
            doctor=self.doctor,
            name="Demo Child",
            guardian_name="Demo Parent",
            guardian_email="parent@example.test",
            guardian_phone="+1-555-0100",
            age_years=7,
            gender="female",
        )
        visit = Visit.objects.create(
            doctor=self.doctor,
            patient=patient,
            clinical_scenario=Visit.SCENARIO_FEVER,
            diagnosis="Fever follow-up",
            consent_confirmed=True,
            transcript="Fever and hydration counseling.",
            doctor_notes="Return if lethargic.",
            status=Visit.STATUS_REVIEW,
        )
        VisitOutput.objects.create(
            visit=visit,
            visit_summary="孩子昨天發燒，今日精神尚可，醫師已說明退燒與補水重點。",
            parent_education="請規律補水、觀察活動力，依醫囑使用退燒藥。",
            patient_education="多喝水並好好休息。",
            parent_summary="孩子昨天發燒，今日精神尚可。",
            child_explanation="多喝水並好好休息。",
            school_note="請規律補水、觀察活動力。",
            warning_signs=["呼吸急促", "精神明顯變差"],
            follow_up_plan="若發燒超過三天或症狀惡化，請回診。",
        )

        payload = {
            "destination": "Udemo",
            "events": [
                {
                    "type": "message",
                    "replyToken": "reply-token",
                    "message": {"type": "text", "id": "1", "text": "查詢 Demo Child parent@example.test"},
                    "source": {"type": "user", "userId": "Uparent"},
                }
            ],
        }
        response = self.post_signed_line_webhook(payload)
        self.assertEqual(response.status_code, 200)
        reply_text = response.json()["replies"][0]["messages"][0]["text"]
        self.assertIn("OpenPediCare 最近一次診後紀錄", reply_text)
        self.assertIn("Demo Child", reply_text)
        self.assertIn("孩子昨天發燒", reply_text)
        self.assertIn(f"https://clinic.example.test/portal/{visit.share_token}/", reply_text)

    @override_settings(
        DEBUG=True,
        LINE_CHANNEL_SECRET="line-test-secret",
        LINE_CHANNEL_ACCESS_TOKEN="",
        LINEBOT_PUBLIC_BASE_URL="https://clinic.example.test",
        LINEBOT_REQUIRE_SIGNATURE=True,
        LINEBOT_ONLY_APPROVED_VISITS=False,
    )
    def test_linebot_previsit_bind_then_latest_lookup_after_visit(self):
        follow_response = self.post_signed_line_webhook(
            {
                "destination": "Udemo",
                "events": [
                    {
                        "type": "follow",
                        "replyToken": "follow-reply",
                        "source": {"type": "user", "userId": "Uparent-previsit"},
                    }
                ],
            }
        )
        self.assertEqual(follow_response.status_code, 200)
        self.assertIn("看診前請先完成 LINE 綁定", follow_response.json()["replies"][0]["messages"][0]["text"])

        bind_response = self.post_signed_line_webhook(
            {
                "destination": "Udemo",
                "events": [
                    {
                        "type": "message",
                        "replyToken": "bind-reply",
                        "message": {"type": "text", "id": "2", "text": "綁定 Demo Child parent@example.test"},
                        "source": {"type": "user", "userId": "Uparent-previsit"},
                    }
                ],
            }
        )
        self.assertEqual(bind_response.status_code, 200)
        self.assertIn("已完成 Demo Child 的 LINE 綁定", bind_response.json()["replies"][0]["messages"][0]["text"])
        self.assertTrue(
            LineParentLink.objects.filter(
                line_user_id="Uparent-previsit",
                child_name="Demo Child",
                guardian_email="parent@example.test",
            ).exists()
        )

        patient = Patient.objects.create(
            doctor=self.doctor,
            name="Demo Child",
            guardian_name="Demo Parent",
            guardian_email="parent@example.test",
            guardian_phone="+1-555-0100",
            age_years=7,
            gender="female",
        )
        visit = Visit.objects.create(
            doctor=self.doctor,
            patient=patient,
            clinical_scenario=Visit.SCENARIO_FEVER,
            diagnosis="Fever follow-up",
            consent_confirmed=True,
            transcript="Fever and hydration counseling.",
            doctor_notes="Return if lethargic.",
            status=Visit.STATUS_REVIEW,
        )
        VisitOutput.objects.create(
            visit=visit,
            visit_summary="看診後摘要：發燒改善中，需補水與觀察精神狀態。",
            parent_education="家長照護：按醫囑用藥、補水、休息。",
            patient_education="多喝水並休息。",
            parent_summary="看診後摘要：發燒改善中。",
            child_explanation="多喝水並休息。",
            school_note="按醫囑用藥、補水、休息。",
            warning_signs=["呼吸急促", "嗜睡"],
            follow_up_plan="若症狀惡化請回診。",
        )

        latest_response = self.post_signed_line_webhook(
            {
                "destination": "Udemo",
                "events": [
                    {
                        "type": "message",
                        "replyToken": "latest-reply",
                        "message": {"type": "text", "id": "3", "text": "最新"},
                        "source": {"type": "user", "userId": "Uparent-previsit"},
                    }
                ],
            }
        )
        self.assertEqual(latest_response.status_code, 200)
        latest_text = latest_response.json()["replies"][0]["messages"][0]["text"]
        self.assertIn("OpenPediCare 最近一次診後紀錄", latest_text)
        self.assertIn("看診後摘要", latest_text)
        self.assertIn(f"https://clinic.example.test/portal/{visit.share_token}/", latest_text)
