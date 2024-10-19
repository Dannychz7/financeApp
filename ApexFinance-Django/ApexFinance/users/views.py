from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Profile, UserStock  # Make sure to import Profile
from .forms import UserRegistrationForm

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Create the user but don't save it yet
            user.set_password(form.cleaned_data['password'])  # Set the password properly
            user.save()  # Now save the user
            Profile.objects.create(user=user)  # Create a profile for the user ***SET profile = Profile.objects.create(user=user) FOR DEBUGGING BELOW***
            
            # Create a default stock entry for NVDA ***USE FOR DEBUGGING***
            # UserStock.objects.create(
            #     profile=profile,
            #     company_name='NVDA',
            #     stock_quantity=10,  # Default quantity
            #     stock_price=250.00   # Default price (you can adjust this as needed)
            # )
            
            messages.success(request, "Registration successful! You can now log in.")  # Optional success message
            return redirect('login')  # Redirect to the login page
    else:
        form = UserRegistrationForm()
    return render(request, 'authentication/register.html', {'form': form})

def login_user(request):
    # Check if the form was submitted
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a dashboard after successful login
            return redirect('dashboard')
        else:
            # Show error message if login fails
            messages.error(request, "There was an error logging in. Try again.")
            return redirect('login')
    else:
        return render(request, 'authentication/login.html', {})