from django import forms
from django.contrib.auth.models import User
import re

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password', 'class': 'form-input'}))
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password', 'class': 'form-input'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter your username', 'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email address', 'class': 'form-input'}),
        }
        labels = {
            'username': '',
            'email': '',
            'password': '',
            'password_confirm': ''
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        username = cleaned_data.get("username")
        email = cleaned_data.get("email")
        
        # Check if email is empty
        if not email:
            email = None
            
        # Optionally, you could also set this as a default value in the model.
        # Check if passwords match
        if password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")

        # Check if password is strong enough (example: at least 8 characters, one digit, one uppercase letter, and one special character)
        if password and len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        
        if password and not re.search(r'\d', password):
            raise forms.ValidationError("Password must contain at least one digit.")
        
        if password and not re.search(r'[A-Z]', password):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        
        if password and not re.search(r'[\W_]', password):  # Special character check (non-alphanumeric)
            raise forms.ValidationError("Password must contain at least one special character.")

        # Check if username is taken
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username is already taken.")
        
        # Check if email is valid and not already used
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email address is already in use.")

        return cleaned_data