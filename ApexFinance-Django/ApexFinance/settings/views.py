from django.http import HttpResponse, HttpResponseRedirect
from datetime import datetime
from django.contrib.auth import logout
from django.shortcuts import redirect, render
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
import os

# User authorization
from django.contrib.auth.decorators import login_required

# Require users to be logged into an account to see their settings
@login_required(login_url='/users/login_user')
def settings(request):
    # Get the currently logged-in user
    user = request.user
    
    # Pass the user object to the template
    return render(request, 'settings/settings.html', {
        'user': user,  # Pass user data to the template
    })

def logoutPage(request):
    if request.method == 'POST':
        logout(request)  # Logs out the user
        return redirect('logoutPage')  # Redirect to the homepage or wherever you want
    return render(request, 'settings/logoutPage.html')  # Render the page if it's a GET request

@login_required(login_url='/users/login_user')
def changePswd(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)  # Keep the user logged in after password change
            messages.success(request, "Your password was updated successfully. You can now use your new password.")
            return redirect('change_pswd')  # Redirect to change password page after success
        else:
            # Check for specific form errors and customize the error messages
            for field, errors in form.errors.items():
                for error in errors: # This line will print all errors in the form
                    messages.error(request, f"Error: {error}")
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'settings/changePswd.html', {'form': form})
