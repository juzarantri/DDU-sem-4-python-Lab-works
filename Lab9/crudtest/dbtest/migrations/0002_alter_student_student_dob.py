# Generated by Django 3.2 on 2021-05-16 07:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbtest', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='student_dob',
            field=models.DateField(blank=True, null=True),
        ),
    ]
