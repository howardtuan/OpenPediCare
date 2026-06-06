from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_patient_gender_visitoutput_parent_education_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="visitoutput",
            name="comic_generated_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="visitoutput",
            name="comic_image",
            field=models.FileField(blank=True, upload_to="comics/%Y/%m/%d/"),
        ),
        migrations.AddField(
            model_name="visitoutput",
            name="comic_prompt",
            field=models.TextField(blank=True),
        ),
    ]
