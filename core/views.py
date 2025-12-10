from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseForbidden
from django.contrib import messages

from .models import Department, Subject, Resource, ApprovedUploader
from .forms import ResourceForm, FacultyCreationForm

from django.views.decorators.http import require_POST
from django.contrib.auth.models import User

# ---------------- REGISTER ----------------
from django.contrib.auth import login
from .forms import StudentRegistrationForm

def register(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('home')

    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto-login the newly registered user
            messages.success(request, "Registration successful! Welcome to StudyBuddy.")
            return redirect('home')
    else:
        form = StudentRegistrationForm()

    return render(request, 'register.html', {'form': form})


# ---------------- HOME ----------------
def home(request):
    departments = Department.objects.all()
    return render(request, 'home.html', {'departments': departments})


# ---------------- DEPARTMENT DETAIL ----------------
@login_required
def department_detail(request, id):
    department = get_object_or_404(Department, id=id)
    subjects = department.subject_set.all()
    return render(request, 'department_detail.html', {'department': department, 'subjects': subjects})



# ---------------- SUBJECT DETAIL ----------------
@login_required
def subject_detail(request, id):
    subject = get_object_or_404(Subject, id=id)

    notes = subject.resource_set.filter(resource_type='note', status='approved')
    pyqs = subject.resource_set.filter(resource_type='pyq', status='approved')
    faculty_notes = subject.resource_set.filter(resource_type='faculty', status='approved')

    context = {
        'subject': subject,
        'notes': notes,
        'pyqs': pyqs,
        'faculty_notes': faculty_notes,
    }
    return render(request, 'subject_detail.html', context)



# ---------------- UPLOAD RESOURCE ----------------
@login_required
def upload_resource(request):

    if request.user.is_staff:
        uploader_role = "faculty"
    else:
        if not ApprovedUploader.objects.filter(student=request.user, is_active=True).exists():
            return HttpResponseForbidden("You are not approved to upload.")
        uploader_role = "student"

    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.uploaded_by = request.user
            resource.status = 'approved' if uploader_role == "faculty" else 'pending'
            resource.save()
            messages.success(request, "Resource uploaded successfully!")
            return redirect('my_uploads')
    else:
        form = ResourceForm()

    departments = Department.objects.all()
    return render(request, 'upload_resource.html', {'form': form, 'departments': departments})


# ---------------- MY UPLOADS ----------------
@login_required
def my_uploads(request):
    uploads = Resource.objects.filter(uploaded_by=request.user)
    return render(request, 'my_uploads.html', {'uploads': uploads})


# ---------------- EDIT RESOURCE ----------------
@login_required
def edit_resource(request, id):
    resource = get_object_or_404(Resource, id=id, uploaded_by=request.user)

    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES, instance=resource)
        if form.is_valid():
            form.save()
            messages.success(request, "Resource updated!")
            return redirect('my_uploads')
    else:
        form = ResourceForm(instance=resource)

    departments = Department.objects.all()
    return render(request, 'upload_resource.html', {'form': form, 'departments': departments})


# ---------------- DELETE RESOURCE ----------------
@login_required
def delete_resource(request, id):
    resource = get_object_or_404(Resource, id=id, uploaded_by=request.user)
    resource.delete()
    messages.success(request, "Resource deleted!")
    return redirect('my_uploads')


# ---------------- FACULTY REVIEW PAGE ----------------
@login_required
def review_uploads(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Only faculty can review uploads.")

    pending = Resource.objects.filter(status='pending')
    return render(request, 'review_uploads.html', {'pending': pending})


@login_required
def approve_upload(request, id):
    if not request.user.is_staff:
        return HttpResponseForbidden("Only faculty can approve uploads.")

    resource = get_object_or_404(Resource, id=id)
    resource.status = 'approved'
    resource.save()
    messages.success(request, "Resource approved!")
    return redirect('review_uploads')


@login_required
def reject_upload(request, id):
    if not request.user.is_staff:
        return HttpResponseForbidden("Only faculty can reject uploads.")

    resource = get_object_or_404(Resource, id=id)
    resource.status = 'rejected'
    resource.save()
    messages.error(request, "Resource rejected.")
    return redirect('review_uploads')


# ---------------- DASHBOARD ----------------
@login_required
def dashboard(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Only faculty can access this page.")

    # All non-faculty users
    students = User.objects.filter(is_staff=False).order_by('id')

    # Attach uploader_status to each student
    for s in students:
        status = ApprovedUploader.objects.filter(student=s).first()
        if status:
            s.uploader_status = status
        else:
            # Create a virtual object so template doesn't break
            class TempStatus:
                is_active = False
                approved_by = None
            s.uploader_status = TempStatus()

    context = {
        'total_departments': Department.objects.count(),
        'total_subjects': Subject.objects.count(),
        'total_resources': Resource.objects.count(),
        'pending_resources': Resource.objects.filter(status='pending').count(),
        'approved_resources': Resource.objects.filter(status='approved').count(),
        'rejected_resources': Resource.objects.filter(status='rejected').count(),

        'students': students,
        'pending_list': Resource.objects.filter(status='pending').order_by('-uploaded_at')[:8],
    }

    return render(request, 'dashboard.html', context)


# ---------------- APPROVE STUDENT UPLOADER ----------------
@login_required
@require_POST
def approve_student_uploader(request, user_id):

    if not request.user.is_staff:
        return HttpResponseForbidden("Only faculty can approve uploaders.")

    student = get_object_or_404(User, id=user_id, is_staff=False)

    entry, created = ApprovedUploader.objects.get_or_create(
        student=student,
        defaults={'approved_by': request.user, 'is_active': True}
    )

    if not created:
        entry.is_active = True
        entry.approved_by = request.user
        entry.save()

    messages.success(request, f"{student.get_full_name() or student.username} approved to upload.")
    return redirect('dashboard')


# ---------------- REVOKE STUDENT UPLOADER ----------------
@login_required
@require_POST
def revoke_student_uploader(request, user_id):

    if not request.user.is_staff:
        return HttpResponseForbidden("Only faculty can revoke uploaders.")

    entry = get_object_or_404(ApprovedUploader, student_id=user_id)
    entry.is_active = False
    entry.save()

    messages.success(request, f"{entry.student.get_full_name() or entry.student.username} permission revoked.")
    return redirect('dashboard')


@login_required
def create_faculty(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Only SuperAdmin can create faculty accounts.")

    if request.method == "POST":
        form = FacultyCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Faculty created successfully!")
            return redirect('dashboard')
    else:
        form = FacultyCreationForm()

    return render(request, "create_faculty.html", {"form": form})