# Generated by Django 5.0.1 on 2024-02-14 09:42

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("social_network", "0004_tag_alter_user_options_alter_user_managers_and_more"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Tag",
        ),
    ]
