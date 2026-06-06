import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Profile(models.Model):
    ROLE_DOCTOR = "doctor"
    ROLE_PARENT = "parent"
    ROLE_CHOICES = (
        (ROLE_DOCTOR, "醫師"),
        (ROLE_PARENT, "家長"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default=ROLE_PARENT)
    display_name = models.CharField(max_length=120, blank=True)
    organization = models.CharField(max_length=160, blank=True)
    signature_text = models.CharField(max_length=160, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.display_name or self.user.username} ({self.role})"


class Patient(models.Model):
    GENDER_CHOICES = (
        ("female", "女"),
        ("male", "男"),
        ("other", "其他"),
        ("unknown", "未填"),
    )
    LANGUAGE_CHOICES = (
        ("zh-Hant", "繁體中文"),
        ("en", "English"),
        ("mixed", "中英文混合"),
    )

    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="patients")
    name = models.CharField(max_length=120)
    guardian_name = models.CharField(max_length=120, blank=True)
    guardian_email = models.EmailField(blank=True)
    guardian_phone = models.CharField(max_length=40, blank=True)
    age_years = models.PositiveSmallIntegerField(default=6)
    gender = models.CharField(max_length=16, choices=GENDER_CHOICES, default="unknown")
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    primary_language = models.CharField(max_length=16, choices=LANGUAGE_CHOICES, default="zh-Hant")
    allergies = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "name"]

    def __str__(self):
        return self.name


class Visit(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_RECORDING = "recording"
    STATUS_PROCESSING = "processing"
    STATUS_REVIEW = "review"
    STATUS_APPROVED = "approved"
    STATUS_CHOICES = (
        (STATUS_DRAFT, "草稿"),
        (STATUS_RECORDING, "錄製中"),
        (STATUS_PROCESSING, "產生中"),
        (STATUS_REVIEW, "待審核"),
        (STATUS_APPROVED, "已發布"),
    )

    SCENARIO_FEVER = "fever"
    SCENARIO_GENERAL = "general"
    SCENARIO_OTITIS = "otitis"
    SCENARIO_VACCINE = "vaccine"
    SCENARIO_ASTHMA = "asthma"
    SCENARIO_CHOICES = (
        (SCENARIO_GENERAL, "一般兒科看診"),
        (SCENARIO_FEVER, "急性發燒"),
        (SCENARIO_OTITIS, "急性中耳炎"),
        (SCENARIO_VACCINE, "疫苗接種門診"),
        (SCENARIO_ASTHMA, "氣喘急性發作"),
    )

    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="visits")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="visits")
    clinical_scenario = models.CharField(max_length=32, choices=SCENARIO_CHOICES)
    diagnosis = models.CharField(max_length=160)
    consent_confirmed = models.BooleanField(default=False)
    transcript = models.TextField(blank=True)
    doctor_notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    share_token = models.CharField(max_length=80, unique=True, editable=False)
    audio_delete_after = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    signed_at = models.DateTimeField(null=True, blank=True)
    signed_by = models.CharField(max_length=160, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.share_token:
            self.share_token = secrets.token_urlsafe(32)
        if not self.audio_delete_after:
            self.audio_delete_after = timezone.now() + timedelta(hours=settings.AUDIO_RETENTION_HOURS)
        super().save(*args, **kwargs)

    @property
    def scenario_label(self):
        return dict(self.SCENARIO_CHOICES).get(self.clinical_scenario, self.clinical_scenario)

    @property
    def child_age_band(self):
        if self.patient.age_years <= 5:
            return "幼兒（3-5 歲）"
        if self.patient.age_years <= 11:
            return "學齡（6-11 歲）"
        return "青少年（12-17 歲）"

    def __str__(self):
        return f"{self.patient.name} - {self.scenario_label} - {self.created_at:%Y-%m-%d}"


class VisitOutput(models.Model):
    visit = models.OneToOneField(Visit, on_delete=models.CASCADE, related_name="output")
    visit_summary = models.TextField(blank=True)
    parent_education = models.TextField(blank=True)
    patient_education = models.TextField(blank=True)
    parent_summary = models.TextField()
    child_explanation = models.TextField()
    school_note = models.TextField()
    warning_signs = models.JSONField(default=list, blank=True)
    follow_up_plan = models.TextField(blank=True)
    comic_image = models.FileField(upload_to="comics/%Y/%m/%d/", blank=True)
    comic_prompt = models.TextField(blank=True)
    comic_generated_at = models.DateTimeField(null=True, blank=True)
    ai_provider = models.CharField(max_length=40, default="mock")
    ai_model = models.CharField(max_length=120, blank=True)
    prompt_version = models.CharField(max_length=40, default="openpedicare-v1")
    generated_at = models.DateTimeField(default=timezone.now)
    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Output for {self.visit}"


class TranscriptChunk(models.Model):
    SOURCE_BROWSER = "browser"
    SOURCE_MANUAL = "manual"
    SOURCE_STT = "stt"
    SOURCE_CHOICES = (
        (SOURCE_BROWSER, "Browser audio"),
        (SOURCE_MANUAL, "Manual transcript"),
        (SOURCE_STT, "Speech-to-text"),
    )

    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, related_name="chunks")
    sequence = models.PositiveIntegerField(default=0)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default=SOURCE_BROWSER)
    text = models.TextField(blank=True)
    audio_file = models.FileField(upload_to="audio/%Y/%m/%d/", blank=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sequence", "created_at"]

    def __str__(self):
        return f"{self.visit_id} chunk {self.sequence}"
