from django.shortcuts import render, redirect, get_object_or_404
from tickets.models import Added
from django.contrib import messages
from .forms import RegistrationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
# from .models import Profile
#
def Register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            messages.success(request, f'{username} your account was created successfully! ')
            login(request, user)
            return redirect('comming_soon')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/signup.html', {'form': form})




@login_required
def Profile(request):
    return render(request, 'accounts/profile.html')

