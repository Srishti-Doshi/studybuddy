from .models import ApprovedUploader

def uploader_status(request):
    if request.user.is_authenticated:
        is_uploader = ApprovedUploader.objects.filter(student=request.user, is_active=True).exists()
        return {'approved_uploader': is_uploader}
    return {'approved_uploader': False}
