# ---------------------- IMPORTS ----------------------
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth import login
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User

from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.functions import Lower

from itertools import groupby

from .models import (
    Department,
    Subject,
    Resource,
    ApprovedUploader,
    TutorialSuggestion,
    Bookmark
)

from .forms import (
    ResourceForm,
    FacultyCreationForm,
    StudentRegistrationForm,
    TutorialForm,
)


# ---------------------- REGISTER ----------------------
def register(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('home')

    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful! Welcome to StudyBuddy.")
            return redirect('home')
    else:
        form = StudentRegistrationForm()

    return render(request, 'register.html', {'form': form})


# ---------------------- HOME ----------------------
def home(request):
    departments = Department.objects.all()
    return render(request, 'home.html', {'departments': departments})


# ---------------------- DEPARTMENT DETAIL ----------------------
@login_required
def department_detail(request, id):
    department = get_object_or_404(Department, id=id)

    # Get subjects grouped by semester
    subjects = Subject.objects.filter(department=department).order_by("semester", "name")

    semesters = {}
    for subject in subjects:
        semesters.setdefault(subject.semester, []).append(subject)

    context = {
        "department": department,
        "semesters": semesters,  # 🔥 grouped data
    }

    return render(request, "department_detail.html", context)



# ---------------------- SUBJECT DETAIL ----------------------
@login_required
def subject_detail(request, id):
    subject = get_object_or_404(Subject, id=id)

    tutorials = TutorialSuggestion.objects.filter(subject=subject)

    notes = Resource.objects.filter(subject=subject, resource_type='note', status='approved')
    pyqs = Resource.objects.filter(subject=subject, resource_type='pyq', status='approved')
    faculty_notes = Resource.objects.filter(subject=subject, resource_type='faculty', status='approved')

    approved_uploader = ApprovedUploader.objects.filter(student=request.user, is_active=True).exists()

    bookmarked_ids = set(
        Bookmark.objects.filter(user=request.user)
        .values_list("resource_id", flat=True)
    )

    context = {
        'subject': subject,
        'notes': notes,
        'pyqs': pyqs,
        'faculty_notes': faculty_notes,
        'tutorials': tutorials,
        'approved_uploader': approved_uploader,
        'bookmarked_ids': bookmarked_ids,
    }
    return render(request, 'subject_detail.html', context)


# ---------------------- ADD TUTORIAL ----------------------
@login_required
def add_tutorial(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)

    if not (
        request.user.is_staff or
        ApprovedUploader.objects.filter(student=request.user, is_active=True).exists()
    ):
        return HttpResponseForbidden("You are not allowed to add tutorials.")

    if request.method == "POST":
        form = TutorialForm(request.POST)
        if form.is_valid():
            tutorial = form.save(commit=False)
            tutorial.subject = subject
            tutorial.added_by = request.user
            tutorial.save()

            messages.success(request, "Tutorial added successfully!")
            return redirect("subject_detail", id=subject.id)
    else:
        form = TutorialForm()

    return render(
        request,
        "add_tutorial.html",
        {"form": form, "subject": subject}
    )

# ---------------------- UPLOAD RESOURCE ----------------------
@login_required
def upload_resource(request):

    if request.user.is_staff:
        uploader_role = "faculty"
    else:
        if not ApprovedUploader.objects.filter(student=request.user, is_active=True).exists():
            return HttpResponseForbidden("You are not approved to upload.")
        uploader_role = "student"

    if request.method == "POST":
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.uploaded_by = request.user
            resource.status = "approved" if uploader_role == "faculty" else "pending"
            resource.save()
            messages.success(request, "Resource uploaded successfully!")
            return redirect("my_uploads")
    else:
        form = ResourceForm()

    return render(request, "upload_resource.html", {"form": form})


# ---------------------- MY UPLOADS ----------------------
@login_required
def my_uploads(request):
    uploads = Resource.objects.filter(uploaded_by=request.user)
    return render(request, "my_uploads.html", {"uploads": uploads})


# ---------------------- EDIT RESOURCE ----------------------
@login_required
def edit_resource(request, id):
    resource = get_object_or_404(Resource, id=id, uploaded_by=request.user)

    if request.method == "POST":
        form = ResourceForm(request.POST, request.FILES, instance=resource)
        if form.is_valid():
            form.save()
            messages.success(request, "Resource updated!")
            return redirect("my_uploads")
    else:
        form = ResourceForm(instance=resource)

    return render(request, "upload_resource.html", {"form": form})


# ---------------------- DELETE RESOURCE ----------------------
@login_required
def delete_resource(request, id):
    resource = get_object_or_404(Resource, id=id, uploaded_by=request.user)
    resource.delete()
    messages.success(request, "Resource deleted!")
    return redirect("my_uploads")


# ---------------------- ADD BOOKMARK ----------------------
@login_required
@require_POST
def add_bookmark(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)

    Bookmark.objects.get_or_create(
        user=request.user,
        resource=resource
    )

    messages.success(request, "Resource bookmarked!")
    return redirect(request.META.get("HTTP_REFERER", "home"))

# ---------------------- REMOVE BOOKMARK ----------------------
@login_required
@require_POST
def remove_bookmark(request, resource_id):
    bookmark = get_object_or_404(
        Bookmark,
        user=request.user,
        resource_id=resource_id
    )
    bookmark.delete()

    messages.info(request, "Bookmark removed.")
    return redirect(request.META.get("HTTP_REFERER", "home"))


# ---------------------- REVIEW UPLOADS (FACULTY) ----------------------
@login_required
def review_uploads(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Only faculty can review uploads.")

    pending = Resource.objects.filter(status="pending")

    return render(request, "review_uploads.html", {"pending": pending})

# ---------------------- APPROVE UPLOAD (FACULTY) ----------------------
@login_required
def approve_upload(request, id):
    if not request.user.is_staff:
        return HttpResponseForbidden("Only faculty can approve uploads.")

    resource = get_object_or_404(Resource, id=id)
    resource.status = "approved"
    resource.save()
    messages.success(request, "Resource approved!")
    return redirect("review_uploads")

# ---------------------- REJECT UPLOAD (FACULTY) ----------------------
@login_required
def reject_upload(request, id):
    if not request.user.is_staff:
        return HttpResponseForbidden("Only faculty can reject uploads.")

    resource = get_object_or_404(Resource, id=id)
    resource.status = "rejected"
    resource.save()
    messages.error(request, "Resource rejected.")
    return redirect("review_uploads")


# ---------------------- DASHBOARD ----------------------
@login_required
def dashboard(request):

    if not request.user.is_staff:
        return HttpResponseForbidden("Only faculty can access dashboard.")

    tab = request.GET.get("tab", "users")

    # --- Registered Users ---
    query = request.GET.get("q", "")
    sort = request.GET.get("sort", "name_asc")

    users = User.objects.filter(is_superuser=False).exclude(id=request.user.id)

    if query:
        users = users.filter(
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
        )

    # Sorting
    if sort == "name_asc":
        users = users.order_by(Lower("first_name"), Lower("last_name"))
    elif sort == "name_desc":
        users = users.order_by(Lower("first_name").desc(), Lower("last_name").desc())
    elif sort == "newest":
        users = users.order_by("-date_joined")
    else:
        users = users.order_by("date_joined")

    # Pagination
    reg_page = request.GET.get("page")
    reg_paginator = Paginator(users, 10)
    reg_page_obj = reg_paginator.get_page(reg_page)

    # Add uploader status
    for u in reg_page_obj:
        u.uploader_status = ApprovedUploader.objects.filter(student=u).first()

    # Promote to faculty tab
    pf_query = request.GET.get("pf_q", "")
    promote_students = User.objects.filter(is_staff=False)

    if pf_query:
        promote_students = promote_students.filter(
            Q(username__icontains=pf_query)
            | Q(first_name__icontains=pf_query)
            | Q(last_name__icontains=pf_query)
            | Q(email__icontains=pf_query)
        )

    pf_page = request.GET.get("pf_page")
    promote_paginator = Paginator(promote_students, 10)
    promote_page_obj = promote_paginator.get_page(pf_page)

    context = {
        "tab": tab,

        "reg_page_obj": reg_page_obj,
        "query": query,
        "sort": sort,

        "promote_page_obj": promote_page_obj,
        "pf_query": pf_query,

        "approved_students": ApprovedUploader.objects.select_related("student", "approved_by"),
        "faculty_list": User.objects.filter(is_staff=True, is_superuser=False),

        "total_departments": Department.objects.count(),
        "total_subjects": Subject.objects.count(),
        "total_resources": Resource.objects.count(),
        "pending_resources": Resource.objects.filter(status="pending").count(),
        "pending_list": Resource.objects.filter(status="pending"),
    }

    return render(request, "dashboard.html", context)


# ---------------------- APPROVE STUDENT UPLOADER ----------------------
@login_required
@require_POST
def approve_student_uploader(request, user_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("Only faculty can approve uploaders.")

    student = get_object_or_404(User, id=user_id, is_staff=False)

    entry, created = ApprovedUploader.objects.get_or_create(
        student=student,
        defaults={"approved_by": request.user, "is_active": True},
    )

    if not created:
        entry.is_active = True
        entry.approved_by = request.user
        entry.save()

    messages.success(request, f"{student.get_full_name() or student.username} is now approved to upload.")
    return redirect("dashboard")


# ---------------------- REVOKE STUDENT UPLOADER ----------------------
@login_required
@require_POST
def revoke_student_uploader(request, user_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("Only faculty can revoke upload access.")

    entry = get_object_or_404(ApprovedUploader, student_id=user_id)
    entry.is_active = False
    entry.save()

    messages.success(request, f"{entry.student.get_full_name() or entry.student.username} upload permission revoked.")
    return redirect("dashboard")


# ---------------------- CREATE FACULTY ----------------------
@login_required
def create_faculty(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Only SuperAdmin can create faculty accounts.")

    if request.method == "POST":
        form = FacultyCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Faculty account created successfully!")
            return redirect("dashboard")
    else:
        form = FacultyCreationForm()

    return render(request, "create_faculty.html", {"form": form})


# ---------------------- MAKE FACULTY ----------------------
@login_required
@require_POST
def make_faculty(request, user_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Only superadmin can assign faculty role.")

    user = get_object_or_404(User, id=user_id)
    user.is_staff = True
    user.save()

    messages.success(request, f"{user.get_full_name() or user.username} promoted to faculty.")
    return redirect("dashboard")


# ---------------------- REMOVE FACULTY ----------------------
@login_required
@require_POST
def remove_faculty(request, user_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Only superadmin can remove faculty role.")

    user = get_object_or_404(User, id=user_id)

    if user == request.user:
        messages.error(request, "You cannot remove your own faculty/superuser status.")
        return redirect("dashboard")

    user.is_staff = False
    user.save()

    messages.success(request, f"{user.get_full_name() or user.username} is no longer a faculty member.")
    return redirect("dashboard")

# ---------------- DELETE RESOURCE (FACULTY / ADMIN) ----------------
@login_required
@require_POST
def delete_resource(request, id):
    resource = get_object_or_404(Resource, id=id)

    if not (request.user.is_staff or request.user == resource.uploaded_by):
        return HttpResponseForbidden()

    resource.delete()
    messages.success(request, "Resource deleted successfully.")
    return redirect(request.META.get("HTTP_REFERER", "home"))


# ---------------- DELETE TUTORIAL ----------------
@login_required
@require_POST
def delete_tutorial(request, tutorial_id):
    tutorial = get_object_or_404(TutorialSuggestion, id=tutorial_id)

    if not (request.user.is_staff or request.user == tutorial.added_by):
        return HttpResponseForbidden()

    tutorial.delete()
    messages.success(request, "Tutorial deleted.")
    return redirect(request.META.get("HTTP_REFERER", "home"))


# ---------------- ABOUT SECTION ----------------
def about(request):
    return render(request, "about.html")

# ---------------- MY BOOKMARKS ----------------
@login_required
def my_bookmarks(request):
    bookmarks = Bookmark.objects.filter(user=request.user).select_related("resource")
    return render(request, "my_bookmarks.html", {
        "bookmarks": bookmarks
    })


from django.http import JsonResponse
from django.views.decorators.http import require_POST

@login_required
@require_POST
def toggle_bookmark_ajax(request):
    resource_id = request.POST.get("resource_id")

    resource = get_object_or_404(Resource, id=resource_id)

    bookmark, created = Bookmark.objects.get_or_create(
        user=request.user,
        resource=resource
    )

    if not created:
        bookmark.delete()
        return JsonResponse({
            "status": "removed",
            "message": "Bookmark removed"
        })

    return JsonResponse({
        "status": "added",
        "message": "Bookmarked"
    })


@login_required
def bookmark_status_api(request):
    bookmarks = Bookmark.objects.filter(user=request.user)\
                                .values_list("resource_id", flat=True)
    return JsonResponse({"bookmarked_ids": list(bookmarks)})