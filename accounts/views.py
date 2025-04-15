from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import ValidationError

# View for logging in
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', '/')  # Jos 'next' on annettu, mene siihen
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('/accounts/login/')


# This function validates the password that it cannot be same as the username and it must at least 8 charecters long
def validate_password(username, password):
    if username.lower() == password.lower():
        raise ValidationError("Password can't bee same as the username")
    if len(password) < 8:
        raise ValidationError("Must be at least 8 chatacters long")
    
    return password



# 4. Cryptographic Failures / Sensitive Data Exposure - this flaw doesn't hash the password when creating a user. 
# the password is exposed if the database were to leak.

# 5. Identification and Authentication Failures - the flaw is that there is no validation for a password.
# This means that user can use a very weak password that is easy to guess
def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            # 5. Fix is to validate password that users tries to use.
            # password = validate_password(username, password)
        
            User.objects.create(username=username, password=password)

            # 4. Fix is to user create_user() instead of create(), because this hashes the password automatically.
            # User.objects.create_user(username=username, password=password)

        except ValidationError as e:
            messages.error(request, f"Error: {e}")


        messages.success(request, 'User created. Please log in.')
        return redirect('/accounts/login/')
    return render(request, 'accounts/register.html')
