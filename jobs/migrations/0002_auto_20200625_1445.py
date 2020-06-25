# Generated by Django 3.0.3 on 2020-06-25 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='job_type',
            field=models.CharField(choices=[('FT', 'Full Time'), ('PT', 'Part Time'), ('IN', 'Intern'), ('CN', 'Contract')], default='FT', max_length=3),
        ),
    ]
