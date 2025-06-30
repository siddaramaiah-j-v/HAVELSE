from django.shortcuts import render, redirect,reverse
from django.utils.safestring import mark_safe
import re
from .forms import RegisterForm,ProfileUpdateForm,OtpRequestForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from .models import User,Profile,OTP
from django.contrib import messages
from django.utils import timezone
from django.utils.timezone import timedelta
from django.contrib.auth import logout,login
from django.core.mail import send_mail
from django.contrib.auth.views import LoginView
from django.contrib.auth import settings
import json

from .utils import clean_phone_number


def superuser_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.is_superuser:
                return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


'''for handling the AJAX calls'''

def check_username(request):
    username = request.GET.get('username')
    exists = User.objects.filter(username=username).exists()
    return JsonResponse({'exists': exists})

def check_phone(request):
    phone = request.GET.get('phone')
    if not re.fullmatch(r'^(?:\+91[\-\s]?|0)?[6-9]\d{9}$', phone):
        return JsonResponse({'error':'enter a valid number'})
    phone = clean_phone_number(phone)
    exists = Profile.objects.filter(phone=phone).exists()
    return JsonResponse({'exists': exists})

def check_email(request):
    email = request.GET.get('email')
    exists = User.objects.filter(email=email).exists()
    return JsonResponse({'exists': exists})


def index(request):
    if request.user.is_authenticated:
        return redirect('login')
    return render(request,'users/index.html')

def register(request):
    if request.method=='POST':
        form=RegisterForm(request.POST)
        if form.is_valid():
            phone=form.cleaned_data.get('phone')
            user = form.save()
            Profile.objects.create(user=user,phone=phone)
            return redirect('users:mail_verification', email=user.email)
    else:
        if request.user.is_authenticated:
            return redirect('login')
        form=RegisterForm()
    return render(request,'users/register.html',{'form':form})


def send_otp(user, otp_code, purpose):
    """Send OTP via email"""
    subject_map = {
        'email_verification': 'Verify Your Email',
        'login': 'Your Login code',
        'password_reset': 'Password Reset OTP'
    }

    subject = subject_map.get(purpose, 'Your OTP')
    message = f'''
    Hello {user.username},

    Your OTP is: {otp_code}

    This OTP will expire in 10 minutes.

    If you didn't request this, please ignore this email.

    Best regards,
    HAVELSE Team
    '''

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

@csrf_protect
@require_http_methods(["GET"])
def mail_verification(request, email=None):
    if not email:
        messages.error(request, 'Email parameter is required.')
        return redirect('register')
    try:
        user = User.objects.get(email=email)
        if user.profile.email_verified:
            messages.info(request, 'Email is already verified. You can login now.')
            return redirect('login')
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('register')
    otp = OTP.objects.create(user=user, purpose='email_verification')
    if not send_otp(user, otp.otp_code, 'email_verification'):
        messages.warning(request,'Registration successful but failed to send OTP for verification.try again later for verification')
        return redirect('login')
    return redirect('users:verify_email', email=user.email)



@csrf_protect
@require_http_methods(["GET", "POST"])
def verify_email(request, email=None):
    """Email verification view"""
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        code = data.get('code')
        if not email:
            return JsonResponse({'success': False, 'message': 'Email required'})
        try:
            user = User.objects.get(email=email)
            if user.profile.email_verified:
                messages.info(request, 'Email is already verified. You can login now.')
                return JsonResponse({'redirect': reverse('login')})
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
            return JsonResponse({'redirect': reverse('register')})
        otp = OTP.objects.filter(
            user=user,
            otp_code=code,
            purpose='email_verification',
            is_used=False
        ).first()

        if not otp:
            return JsonResponse({'success': False, 'message': 'Invalid OTP. Please try again.'})

        if otp.is_expired():
            return JsonResponse({'success': False, 'message': 'OTP has expired. Please request a new one.'})

        otp.is_used = True
        otp.save()

        user.profile.email_verified = True
        user.profile.save()

        messages.success(request, 'Email verified successfully! You can now login.')
        return JsonResponse({'success': True})

    if not email:
        messages.error(request, 'Email parameter is required.')
        return redirect('register')
    try:
        user = User.objects.get(email=email)
        if user.profile.email_verified:
            messages.info(request, 'Email is already verified. You can login now.')
            return redirect('login')
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('register')
    return render(request, 'users/verify.html', {'email': email})


@csrf_protect
def resend_verification_otp(request, email):
    """Resend email verification OTP"""
    if request.method=='POST':
        try:
            user = User.objects.get(email=email)
            if user.profile.email_verified:
                messages.info(request, 'Email is already verified.')
                return JsonResponse({'redirect': reverse('login')})

            # Invalidate previous OTPs
            OTP.objects.filter(
                user=user,
                purpose='email_verification',
                is_used=False
            ).update(is_used=True)
            if OTP.has_exceeded_limit(user,'email-verification'):
                return JsonResponse({'success': False, 'message': 'You have reached the OTP limit. Try again after some time.'})
            otp=OTP.objects.create(user=user,purpose='email_verification')

            if send_otp(user, otp.otp_code, 'email_verification'):
                return JsonResponse({'success': True,'message':'New verification OTP sent to your email.'})
            else:
                messages.error(request, 'Failed to send OTP. Please try again.')
                return JsonResponse({'success': False, 'message': 'Failed to send OTP. Please try again.'})
        except User.DoesNotExist:
            messages.error(request, 'No user with this email')
            return JsonResponse({'redirect': reverse('login')})


class CustomLoginView(LoginView):
    template_name = 'users/login.html'

    def form_valid(self, form):
        user = form.get_user()
        if not user.profile.email_verified:
            verify_url = reverse('users:mail_verification', kwargs={'email': user.email})
            messages.error(self.request, mark_safe(f'Please verify your email before logging in. <a href="{verify_url}">click here</a>'))
            return redirect('login')
        return super().form_valid(form)


@csrf_protect
@require_http_methods(["GET", "POST"])
def login_request(request):
    """Request login OTP view"""
    if request.method == 'POST':
        form = OtpRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                if not user.profile.email_verified:
                    verify_url = reverse('users:mail_verification', kwargs={'email': user.email})
                    messages.error(request, mark_safe(f'Please verify your email first. <a href="{verify_url}">click here</a>'))
                    return redirect('login_request')


                OTP.objects.filter(
                    user=user,
                    purpose='login',
                    is_used=False
                ).update(is_used=True)

                if OTP.has_exceeded_limit(user, 'login'):
                    messages.info(request,'You have reached the OTP limit. Try again after some time')
                    return redirect('login_request')
                otp = OTP.objects.create(user=user, purpose='login')

                if send_otp(user, otp.otp_code, 'login'):
                    return redirect('users:verify_login', email=email)
                else:
                    messages.info(request, 'Failed to send OTP. Please try again.')
                    return redirect('login_request')
            except User.DoesNotExist:
                messages.error(request,'No account found with this email address.')
                return redirect('login_request')
    else:
        form = OtpRequestForm()
    return render(request, 'users/otp_login.html', {'form': form})


@csrf_protect
@require_http_methods(["GET", "POST"])
def verify_login(request, email=None):
    """Verify login OTP view"""
    if not email:
        messages.error(request, 'Email parameter is required.')
        return JsonResponse({'redirect': reverse('login_request')})

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return JsonResponse({'redirect': reverse('login_request')})

    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        code = data.get('code')

        if not email:
            return JsonResponse({'success': False, 'message': 'Email required'})
        otp = OTP.objects.filter(
            user=user,
            otp_code=code,
            purpose='login',
            is_used=False
        ).first()

        if not otp:
            return JsonResponse({'success': False, 'message': 'Invalid OTP. Please try again.'})

        if otp.is_expired():
            return JsonResponse({'success': False, 'message': 'OTP has expired. Please request a new one.'})
        login(request,user,backend='django.contrib.auth.backends.ModelBackend')
        otp.is_used = True
        otp.save()
        return JsonResponse({'success': True})

    return render(request, 'users/login_code.html', {'email': email})


@csrf_protect
def resend_login_otp(request, email):
    """Resend login OTP"""
    if request.method=='POST':
        try:
            user = User.objects.get(email=email)
            if not user.profile.email_verified:
                verify_url = reverse('users:mail_verification', kwargs={'email': user.email})
                messages.error(request,mark_safe(f'Please verify your email before logging in. <a href="{verify_url}">click here</a>'))
                return JsonResponse({'redirect': reverse('login_request')})
            # Invalidate previous OTPs
            OTP.objects.filter(
                user=user,
                purpose='login',
                is_used=False
            ).update(is_used=True)

            if OTP.has_exceeded_limit(user, 'login'):
                return JsonResponse({'success': False, 'message': 'You have reached the OTP limit. Try again after some time.'})
            otp = OTP.objects.create(user=user, purpose='login')

            if send_otp(user, otp.otp_code, 'login'):
                return JsonResponse({'success': True, 'message': 'OTP sent to your email.'})
            else:
                messages.error(request, 'Failed to send OTP. Please try again.')
                return JsonResponse({'success': False, 'message': 'Failed to send OTP. Please try again.'})
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email address.')
            return JsonResponse({'redirect': reverse('login_request')})


@login_required
def edit(request):
    if request.method=='POST':
        profile=Profile.objects.get(user=request.user)
        form=ProfileUpdateForm(request.POST,request.FILES,instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "your profile updated successfully")
            return redirect('users:edit')
        else:
            messages.error(request, f"enter proper details")
            return redirect('users:edit')
    form=ProfileUpdateForm(instance=request.user)
    return render(request,'users/edit.html',{'form':form,'hide_nav':True})

@login_required
def account_deletion(request):
    if request.method=='POST':
        print(request.headers)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            password = request.POST.get("password")
            user = request.user
            if  not user.check_password(password):
                return JsonResponse({'success': False,'message': 'Incorrect password'}, status=400)

            user.profile.deactivated_at = timezone.now()
            user.profile.save()
            logout(request)
            messages.success(request, "Account deactivated. You can reactivate within 10 days by logging in again.")
            return JsonResponse({'success': True,'message': 'Account deactivated successfully','redirect_url': f"{reverse('login')}"})
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)



@login_required
@superuser_required
def delete_accounts(request):
    try:
        grace_period = timedelta(days=10)
        cutoff_date = timezone.now() - grace_period
        deactivated_profiles = User.objects.filter(profile__deactivated_at__lt=cutoff_date,).select_related('profile')
        # count = deactivated_profiles.count()
        for user in deactivated_profiles:
            user.is_active=False
            user.save()
        # messages.success(request,f'deleted {count} accounts')
    except Exception as e:
        messages.error(request,f"error:{e}")
    return redirect(reverse('learn:home'))
