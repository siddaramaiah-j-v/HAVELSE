from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import Profile
from django.contrib.auth.forms import UserCreationForm

class RegisterForm(UserCreationForm):
    email=forms.EmailField()
    name=forms.CharField(min_length=3,max_length=10)
    phone=forms.IntegerField()

    class Meta:
        model=User
        fields=['email','username','password1','password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Default classes and ids for all fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'id':field_name,
                'placeholder':f'enter your {field_name}'
            })

        self.fields['password1'].widget.attrs.update({
            'placeholder':'enter a password'
        })
        
        self.fields['password2'].widget.attrs.update({
            'placeholder':'confirm your password'
        })

    def clean_email(self):
        email=self.cleaned_data.get('email')
        if Profile.objects.filter(email=email).exists():
            raise ValidationError('email already in use')
        return email
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if Profile.objects.filter(phone=phone).exists():
            raise ValidationError('Phone number already registered')
        return phone



class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile information.
    Only allows editing name, bio, and profile image.
    """

    class Meta:
        model = Profile
        fields = ['email','name','gender','bio','image']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
            'gender':forms.Select(attrs={
                'class':'form-select',
                'id':'gender'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].disabled = True

