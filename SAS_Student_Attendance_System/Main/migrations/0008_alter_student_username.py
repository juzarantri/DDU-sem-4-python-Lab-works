# Generated by Django 3.2 on 2021-06-01 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Main', '0007_alter_student_roll_no'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='username',
            field=models.CharField(default='', max_length=30, unique=True),
        ),
    ]
