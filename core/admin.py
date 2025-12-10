from django.contrib import admin
from .models import Department, Subject, Resource, ApprovedUploader

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'semester')
    list_filter = ('department', 'semester')


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'resource_type', 'uploaded_by', 'status', 'uploaded_at')
    list_filter = ('resource_type', 'status', 'subject')


@admin.register(ApprovedUploader)
class ApprovedUploaderAdmin(admin.ModelAdmin):
    list_display = ('student', 'approved_by', 'is_active', 'created_at')
    list_filter = ('is_active',)
