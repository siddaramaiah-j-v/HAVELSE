from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from .models import Profile
from django.contrib.auth.forms import UserCreationForm

class RegisterForm(UserCreationForm):
    phone=forms.CharField(max_length=15,validators=[RegexValidator(regex=r'^(?:\+91[\-\s]?|0)?[6-9]\d{9}$',message='Enter a valid phone number.',)])

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
        if User.objects.filter(email=email).exists():
            raise ValidationError('email already in use')
        if email and not email.lower().endswith('@gmail.com'):
            raise ValidationError('Only Gmail addresses are allowed.')
        return email
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        import re
        digits = re.sub(r'\D', '', phone)  # keep only digits

        if digits.startswith('91') and len(digits) == 12:
            digits = digits[2:]
        elif digits.startswith('0') and len(digits) == 11:
            digits = digits[1:]

        if not re.fullmatch(r'[6-9]\d{9}', digits):
            raise forms.ValidationError("Enter a valid 10-digit Indian mobile number.")
        if Profile.objects.filter(phone=phone).exists():
            raise ValidationError('number already registered')
        return digits



class ProfileUpdateForm(forms.ModelForm):
    """
    Form for updating user profile information Only allows editing name, bio, and profile image.
    """

    class Meta:
        model = Profile
        fields = ['name','gender','bio','image']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
            'gender':forms.Select(attrs={
                'class':'form-select form-control',
                'id':'gender'
            })
        }

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['email'].disabled = True

class OtpRequestForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}))