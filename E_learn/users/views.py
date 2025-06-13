from django.shortcuts import render, redirect,reverse
from .forms import RegisterForm,ProfileUpdateForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import User,Profile
from django.contrib import messages
from django.utils import timezone
from django.utils.timezone import timedelta
from django.contrib.auth import logout



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
    exists = Profile.objects.filter(phone=phone).exists()
    return JsonResponse({'exists': exists})

def check_email(request):
    email = request.GET.get('email')
    exists = Profile.objects.filter(email=email).exists()
    return JsonResponse({'exists': exists})


def index(request):
    if request.user.is_authenticated:
        return redirect('login')
    return render(request,'users/index.html')

def register(request):
    if request.method=='POST':
        form=RegisterForm(request.POST)
        if form.is_valid():
            name=form.cleaned_data.get('name')
            phone=form.cleaned_data.get('phone')
            email=form.cleaned_data.get('email')
            user=form.save()
            Profile.objects.create(user=user,name=name,email=email,phone=phone)
            messages.success(request,f"welcome {user}!,registered successfully")
            return redirect('login')
    else:
        if request.user.is_authenticated:
            return redirect('login')
        form=RegisterForm()
    return render(request,'users/register.html',{'form':form})

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
    form=ProfileUpdateForm(instance=request.user)
    return render(request,'users/edit.html',{'form':form})

@login_required
def account_deletion(request):
    if request.method=='POST':
        password = request.POST.get("password")
        user = request.user
        if not password:
            messages.error(request, "Please enter your password.")
            return redirect(reverse('users:edit'))
        if user.check_password(password):
            user.profile.deactivated_at = timezone.now()
            user.profile.save()
            logout(request)
            messages.success(request, "Account deactivated. You can reactivate within 30 days by logging in again.")
            return redirect("login")
        else:
            messages.error(request, "Incorrect password. Please try again.")
            return redirect(reverse('users:edit'))

@login_required
@superuser_required
def delete_accounts(request):
    try:
        grace_period = timedelta(days=30)
        cutoff_date = timezone.now() - grace_period
        deactivated_profiles = User.objects.filter(profile__deactivated_at__lt=cutoff_date,).select_related('profile')
        # count = deactivated_profiles.count()
        for user in deactivated_profiles:
            user.is_active=False
        # messages.success(request,f'deleted {count} accounts')
    except Exception as e:
        messages.error(request,f"error:{e}")
    return redirect(reverse('learn:home'))
