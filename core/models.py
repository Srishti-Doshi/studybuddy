from django.db import models
from django.contrib.auth.models import User


# ---------------------- DEPARTMENT ----------------------
class Department(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="department_images/", blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


# ---------------------- SUBJECT ----------------------
class Subject(models.Model):
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="subjects"
    )
    name = models.CharField(max_length=200)
    semester = models.IntegerField()

    class Meta:
        ordering = ["semester", "name"]
        unique_together = ("department", "name", "semester")

    def __str__(self):
        return f"{self.name} (Sem {self.semester})"


# ---------------------- RESOURCE (NOTES / PYQ / FACULTY NOTES) ----------------------
class Resource(models.Model):

    RESOURCE_TYPES = [
        ('note', 'Notes'),
        ('pyq', 'Previous Year Question'),
        ('faculty', 'Faculty Notes'),
    ]
    

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="resources"
    )
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='resources/')
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    description = models.TextField(blank=True, null=True)

    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending'
    )

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.title


# ---------------------- STUDENT APPROVAL FOR UPLOADS ----------------------
class ApprovedUploader(models.Model):
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="uploader_profile"
    )
    approved_by = models.ForeignKey(
        User, related_name='approved_students', on_delete=models.SET_NULL, null=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Uploader: {self.student.username}"


# ---------------------- TUTORIAL SUGGESTION ----------------------
class TutorialSuggestion(models.Model):

    RESOURCE_TYPES = [
        ('video', 'Video Tutorial'),
        ('playlist', 'Playlist'),
        ('article', 'Article / Blog'),
        ('pdf', 'PDF Resource'),
        ('website', 'Website'),
    ]

    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="tutorials"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    link = models.URLField()
    resource_type = models.CharField(
        max_length=20, choices=RESOURCE_TYPES, default='video'
    )

    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
    
    
# ---------------------- BOOKMARK ----------------------
class Bookmark(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bookmarks"
    )
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name="bookmarked_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "resource")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} bookmarked {self.resource.title}"

