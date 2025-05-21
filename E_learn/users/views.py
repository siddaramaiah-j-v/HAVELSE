from django.shortcuts import render, redirect,reverse
from .forms import RegisterForm,ProfileUpdateForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import User,Profile
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
'''for handling the AJAX calls'''


def check_username(request):
    username = request.GET.get('username')
    exists = User.objects.filter(username=username).exists()
    return JsonResponse({'exists': exists})


def check_email(request):
    email = request.GET.get('email')
    exists = Profile.objects.filter(email=email).exists()
    return JsonResponse({'exists': exists})


def index(request):
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
        if user.check_password(password):
            user.profile.deactivated_at = timezone.now()
            user.profile.save()
            logout(request)
            messages.success(request, "Account deactivated. You can reactivate within 30 days by logging in again.")
            return redirect("login")
        else:
            messages.error(request, "Incorrect password. Please try again.")
            return redirect(reverse('users:edit'))