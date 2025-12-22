from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Department,
    Subject,
    Resource,
    ApprovedUploader,
    TutorialSuggestion,
    Bookmark
)


# ---------------------- DEPARTMENT ADMIN ----------------------
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "image_preview")
    search_fields = ("name",)
    list_filter = ("name",)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="60" height="40" style="border-radius:4px; object-fit:cover;" />',
                obj.image.url
            )
        return "No Image"
    image_preview.short_description = "Preview"


# ---------------------- SUBJECT ADMIN ----------------------
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "department", "semester")
    list_filter = ("department", "semester")
    search_fields = ("name",)


# ---------------------- RESOURCE ADMIN ----------------------
@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "resource_type", "uploaded_by", "status", "uploaded_at")
    list_filter = ("resource_type", "status", "subject")
    search_fields = ("title", "description")

    readonly_fields = ("uploaded_at",)

    fieldsets = (
        ("Resource Info", {
            "fields": ("title", "subject", "resource_type", "file", "description")
        }),
        ("Upload Details", {
            "fields": ("uploaded_by", "status", "uploaded_at")
        }),
    )


# ---------------------- APPROVED UPLOADER ADMIN ----------------------
@admin.register(ApprovedUploader)
class ApprovedUploaderAdmin(admin.ModelAdmin):
    list_display = ("student", "approved_by", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("student__username",)

    readonly_fields = ("created_at",)


# ---------------------- TUTORIAL SUGGESTION ADMIN ----------------------
@admin.register(TutorialSuggestion)
class TutorialSuggestionAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "resource_type", "added_by", "created_at", "open_link")
    list_filter = ("subject", "resource_type")
    search_fields = ("title", "description")

    readonly_fields = ("created_at",)

    def open_link(self, obj):
        return format_html(
            '<a href="{}" target="_blank" style="color:#0d6efd;">Open</a>',
            obj.link
        )
    open_link.short_description = "Tutorial Link"


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ("user", "resource", "created_at")
    search_fields = ("user__username", "resource__title")
