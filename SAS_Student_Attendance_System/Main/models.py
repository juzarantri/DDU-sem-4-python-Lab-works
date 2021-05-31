from django.contrib.auth.models import AbstractUser, User
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

class Student(models.Model):
    username = models.CharField(max_length=30, unique=True)
    fullname = models.CharField(max_length=60)
    phone_no = PhoneNumberField()
    parents_phone_no = PhoneNumberField()
    branch = models.CharField(max_length=30)
    semester = models.CharField(max_length=30, default="empty")
    student_id = models.CharField(max_length=30, unique=True)
    roll_no = models.CharField(max_length=30)
    is_teacher = models.CharField(max_length=30, default="no")
    user = models.OneToOneField(User,on_delete=models.CASCADE,null=True)

class Teacher(models.Model):
    username = models.CharField(max_length=30, unique=True)
    fullname = models.CharField(max_length=60)
    phone_no = PhoneNumberField()
    is_teacher = models.CharField(max_length=30, default="yes")
    user = models.OneToOneField(User,on_delete=models.CASCADE,null=True)

