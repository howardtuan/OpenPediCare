from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0003_visitoutput_comic_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="visitoutput",
            name="prompt_version",
            field=models.CharField(default="openpedicare-v1", max_length=40),
        ),
    ]
