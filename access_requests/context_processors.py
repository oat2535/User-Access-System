from .models import AccessRequest

def pending_approvals_count(request):
    if request.user.is_authenticated and request.user.is_staff:
        count = AccessRequest.objects.filter(status__in=['pending_manager', 'pending_it']).count()
        return {'pending_approval_count': count}
    return {}
