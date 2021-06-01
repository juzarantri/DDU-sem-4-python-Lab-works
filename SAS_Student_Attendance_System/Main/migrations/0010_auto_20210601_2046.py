# Generated by Django 3.2 on 2021-06-01 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Main', '0009_alter_student_username'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='id',
        ),
        migrations.AlterField(
            model_name='student',
            name='username',
            field=models.CharField(max_length=30, primary_key=True, serialize=False, unique=True),
        ),
    ]