# Generated by Django 5.2 on 2025-06-07 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_profile_deactivated_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='gender',
            field=models.CharField(blank=True, choices=[('M', 'male'), ('F', 'female'), ('O', 'prefer not to say')], max_length=1),
        ),
    ]
