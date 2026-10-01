from django import forms
from .models import User

class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control border-left-0', 
            'placeholder': 'example@mail.com',
            'autocomplete': 'email',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control border-left-0', 
            'placeholder': '••••••••',
            'autocomplete': 'current-password'
        })
    )

class RegisterForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control border-left-0', 
            'placeholder': 'example@mail.com',
            'autocomplete': 'email',
            'autofocus': True
        })
    )

    username = forms.CharField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control border-left-0', 
            'placeholder': 'Username',
            'autocomplete': 'username'
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control border-left-0', 
            'placeholder': '••••••••',
            'autocomplete': 'current-password'
        })
    )

    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control border-left-0', 
            'placeholder': '••••••••',
            'autocomplete': 'current-password-confirm'
        })
    )

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'avatar')

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control-file'}),
        }
