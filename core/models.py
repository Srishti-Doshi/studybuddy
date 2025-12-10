from django.db import models
from django.contrib.auth.models import User

class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Subject(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    semester = models.IntegerField()

    def __str__(self):
        return self.name


class Resource(models.Model):
    RESOURCE_TYPES = [
        ('note', 'Note'),
        ('pyq', 'Previous Year Question'),
        ('faculty', 'Faculty Note'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='resources/')
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    description = models.TextField(blank=True, null=True)

    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return self.title


class ApprovedUploader(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    approved_by = models.ForeignKey(User, related_name='approved_students', on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.student.username
