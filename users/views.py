import re

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProfileUpdateForm, UserUpdateForm, UserRegisterForm

from .models import Profile


def email_check(user_cred):
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if re.search(regex, user_cred):
        return True
    else:
        return None


# login
def my_login(request):
    if request.POST:
        user_cred = request.POST['username']
        password = request.POST['password']
        if email_check(user_cred):
            username = User.objects.get(email=user_cred).username
            user = authenticate(request, username=username, password=password)
        else:
            user = authenticate(request, username=user_cred, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You have logged into your account!!')
            return redirect('home')

        else:
            messages.error(request, 'Invalid Credential')
            return redirect(request.META['HTTP_REFERER'])
    else:
        return render(request, 'authorization/login.html', {'title': "Login"})


# register
def my_register(request):
    if request.POST:
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')
            form.save()
            return redirect('login')
    else:
        form = UserRegisterForm()

    context = {
        'form': form
    }
    return render(request, 'authorization/register.html', context)


# logout
def my_logout(request):
    logout(request)
    return redirect('index')


# single profile page for all functionality, if the pid=request.user.id, can show the form, else only the details are shown, not showing winnings as of now
def my_profile(request, pid):
    global u_form, p_form, profile
    user = get_object_or_404(User, id=pid)
    if request.POST and request.user == user:
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your Account has been Updated')
            return redirect('profile', pid=pid)
    elif request.GET and request.user.id == pid:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    else:
        profile = get_object_or_404(Profile, user=user)
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'user': user,
        'profile': profile,
        'title': "Profile",
    }
    return render(request, 'profile/profile.html', context=context)


# show all them members in the profile
def members(request):
    p = Profile.objects.all()
    return render(request, 'profile/members.html', context={'profile': p})
