from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import make_faculty, register, remove_faculty, add_tutorial


from core.views import (
    home, department_detail, subject_detail,
    upload_resource, my_uploads, edit_resource, delete_resource,
    review_uploads, approve_upload, reject_upload,
    dashboard, approve_student_uploader, revoke_student_uploader, create_faculty
)

from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', home, name='home'),
    path('department/<int:id>/', department_detail, name='department_detail'),
    path('subject/<int:id>/', subject_detail, name='subject_detail'),

    path('upload/', upload_resource, name='upload_resource'),
    path('my-uploads/', my_uploads, name='my_uploads'),
    path('edit/<int:id>/', edit_resource, name='edit_resource'),
    path('delete/<int:id>/', delete_resource, name='delete_resource'),

    path('review/', review_uploads, name='review_uploads'),
    path('approve/<int:id>/', approve_upload, name='approve_upload'),
    path('reject/<int:id>/', reject_upload, name='reject_upload'),

    path('dashboard/', dashboard, name='dashboard'),
    path('approve-student/<int:user_id>/', approve_student_uploader, name='approve_student_uploader'),
    path('revoke-student/<int:user_id>/', revoke_student_uploader, name='revoke_student_uploader'),

    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', register, name='register'),

    path('create-faculty/', create_faculty, name="create_faculty"),

    path("make-faculty/<int:user_id>/", make_faculty, name="make_faculty"),
    path("remove-faculty/<int:user_id>/", remove_faculty, name="remove_faculty"),

    path("subject/<int:subject_id>/add_tutorial/", add_tutorial, name="add_tutorial"),

    path('', include('core.urls')),
    # path('', include('api.urls')),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
