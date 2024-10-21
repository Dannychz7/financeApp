from django import forms
from django.contrib.auth.models import User

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")
        
class BuyStockForm(forms.Form):
    company_name = forms.CharField(max_length=255, label='Company Name')
    stock_quantity = forms.IntegerField(min_value=1, label='Quantity')

class SellStockForm(forms.Form):
    company_name = forms.CharField(max_length=255, label='Company Name')
    stock_quantity = forms.IntegerField(min_value=1, label='Quantity')