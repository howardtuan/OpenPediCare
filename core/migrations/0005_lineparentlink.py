from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0004_alter_visitoutput_prompt_version"),
    ]

    operations = [
        migrations.CreateModel(
            name="LineParentLink",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("line_user_id", models.CharField(db_index=True, max_length=80)),
                ("child_name", models.CharField(max_length=120)),
                ("guardian_email", models.EmailField(blank=True, max_length=254)),
                ("guardian_phone", models.CharField(blank=True, max_length=40)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("last_lookup_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "ordering": ["-updated_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="lineparentlink",
            constraint=models.UniqueConstraint(
                fields=("line_user_id", "child_name", "guardian_email", "guardian_phone"),
                name="unique_line_parent_child_contact",
            ),
        ),
    ]
