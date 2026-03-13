from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.admin.views.decorators import staff_member_required
from .models import AccessRequest, System, AccessRequestLog
from .forms import AccessRequestForm
from django.core.mail import send_mail
from django.conf import settings

def log_action(request, access_request, action, details=''):
    AccessRequestLog.objects.create(
        access_request=access_request,
        actor=request.user,
        action=action,
        details=details
    )

def send_notification_email(access_request, subject, message):
    try:
        # Check if email is configured (simulated for now if not in settings)
        # In production, ensure EMAIL_HOST etc. are set in settings.py
        recipient_list = [access_request.email]
        if access_request.user and access_request.user.email:
            recipient_list.append(access_request.user.email)
            
        send_mail(
            subject=f"[Access Request] {subject}",
            message=message,
            from_email=None, # Use default
            recipient_list=list(set(recipient_list)), # Unique
            fail_silently=True
        )
    except Exception as e:
        print(f"Failed to send email: {e}")

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def dashboard(request):
    # If superuser or staff, show all requests? Or just show my requests?
    # Logic: Dashboard shows *my* requests. Admin panel shows *all*.
    # Image suggests singular user view.
    
    requests = AccessRequest.objects.filter(user=request.user).order_by('-created_at')
    
    pending_count = requests.filter(status='pending').count()
    approved_count = requests.filter(status='approved').count()
    rejected_count = requests.filter(status='rejected').count()
    
    context = {
        'requests': requests[:10], # Show recent 10
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
    }
    return render(request, 'access_requests/dashboard.html', context)

@login_required
def request_list(request):
    requests = AccessRequest.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'access_requests/request_list.html', {'requests': requests})

@login_required
def create_request(request):
    if request.method == 'POST':
        form = AccessRequestForm(request.POST)
        if form.is_valid():
            access_request = form.save(commit=False)
            access_request.user = request.user
            access_request.save()
            form.save_m2m() # Required for saving ManyToManyField
            
            # Log and Notify
            log_action(request, access_request, 'Created', 'Created new request')
            send_notification_email(access_request, "Received Request", f"Your request {access_request.request_code} has been received and is pending manager approval.")
            
            return redirect('dashboard')
    else:
        # Pre-fill email if available
        initial_data = {}
        if request.user.email:
            initial_data['email'] = request.user.email
        form = AccessRequestForm(initial=initial_data)
    return render(request, 'access_requests/request_form.html', {'form': form})

@login_required
def request_detail(request, pk):
    access_request = get_object_or_404(AccessRequest, pk=pk)
    if access_request.user != request.user and not request.user.is_superuser:
        return redirect('dashboard')
        
    return render(request, 'access_requests/request_detail.html', {'request_obj': access_request})

# Manager / Admin Views

@staff_member_required
def approval_list(request):
    from django.core.paginator import Paginator

    # Manager sees 'pending_manager', IT sees 'pending_it'
    # Simplified: Staff sees all pending
    request_list = AccessRequest.objects.filter(status__in=['pending_manager', 'pending_it']).order_by('-created_at')
    
    paginator = Paginator(request_list, 5) # Show 5 requests per page
    page_number = request.GET.get('page')
    requests = paginator.get_page(page_number)
    
    return render(request, 'access_requests/approval_list.html', {'requests': requests})

@staff_member_required
def approve_request(request, pk):
    if request.method == 'POST':
        access_request = get_object_or_404(AccessRequest, pk=pk)
        
        if access_request.status == 'pending_manager':
            # Manager Approval -> Send to IT
            access_request.status = 'pending_it'
            access_request.manager_approver = request.user
            access_request.manager_approval_date = timezone.now()
            access_request.manager_comment = request.POST.get('comment', '')
            access_request.save()
            
            log_action(request, access_request, 'Manager Approved', f"Comment: {access_request.manager_comment}")
            send_notification_email(access_request, "Manager Approved", f"Your request {access_request.request_code} has been approved by Manager. Waiting for IT approval.")
            
        elif access_request.status == 'pending_it':
            # IT Approval -> Final Approved
            access_request.status = 'approved'
            access_request.it_approver = request.user
            access_request.it_approval_date = timezone.now()
            # access_request.it_comment = request.POST.get('comment', '') # If needed
            access_request.save()
            
            log_action(request, access_request, 'IT Approved', "Final Approval")
            send_notification_email(access_request, "Access Granted", f"Congratulations! Your request {access_request.request_code} has been fully approved.")
            
    return redirect('approval_list')

@staff_member_required
def reject_request(request, pk):
    if request.method == 'POST':
        access_request = get_object_or_404(AccessRequest, pk=pk)
        previous_status = access_request.status
        access_request.status = 'rejected'
        access_request.reject_reason = request.POST.get('reason', '')
        
        # Record who rejected
        access_request.rejected_by = request.user
        access_request.rejected_at = timezone.now()
        
        if previous_status == 'pending_manager':
            access_request.manager_approver = request.user 
        elif previous_status == 'pending_it':
            access_request.it_approver = request.user
            
        access_request.save()
        
        log_action(request, access_request, 'Rejected', f"Reason: {access_request.reject_reason}")
        send_notification_email(access_request, "Request Rejected", f"Your request {access_request.request_code} has been rejected. Reason: {access_request.reject_reason}")

    return redirect('approval_list')

def public_create_request(request):
    """
    Allow users to request access without logging in.
    """
    if request.method == 'POST':
        form = AccessRequestForm(request.POST)
        if form.is_valid():
            access_request = form.save(commit=False)
            access_request.user = None # Public request has no user initially
            access_request.save()
            form.save_m2m()
            
            # Log action (actor is None for public)
            AccessRequestLog.objects.create(
                access_request=access_request,
                actor=None,
                action='Created (Public)',
                details='Created new request via public form'
            )
            
            # Send email
            send_notification_email(access_request, "Received Request", f"Your request {access_request.request_code} has been received and is pending manager approval.")
            
            return render(request, 'access_requests/request_success.html', {'request_code': access_request.request_code})
    else:
        form = AccessRequestForm()
    return render(request, 'access_requests/request_form.html', {'form': form, 'is_public': True})
