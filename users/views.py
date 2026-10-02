from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import get_user_model, authenticate, login, logout as django_logout
from django.views.decorators.http import require_POST

from .forms import LoginForm, RegisterForm, UserForm

User = get_user_model()

class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('blogs-post-list')
        return render(request, 'users/register.html')

    def post(self, request):
        form = RegisterForm(data=request.POST)
        if form.is_valid():
            email = form.data.get('email')
            username = form.data.get('username')
            password = form.data.get('password')
            password_confirm = form.data.get('password_confirm')

            context = {'email': email, 'username': username}

            if password != password_confirm:
                context['error'] = "Пароли не совпадают"
                return render(request, 'users/register.html', context)

            if User.objects.filter(email=email).exists():
                context['error'] = "Пользователь с таким Email уже зарегистрирован"
                return render(request, 'users/register.html', context)

            if User.objects.filter(username=username).exists():
                context['error'] = "Это имя пользователя уже занято"
                return render(request, 'users/register.html', context)

            try:
                user = User.objects.create_user(email=email, username=username, password=password)
                login(request, user)
                return redirect('blogs-post-list')
            except Exception as e:
                context['error'] = f"Ошибка при регистрации"
                return render(request, 'users/register.html', context)

class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('blogs-post-list')
        form = LoginForm()
        return render(request, 'users/login.html', context={"form": form})

    def post(self, request):
        form = LoginForm(data=request.POST)
        if form.is_valid():
            email = form.data.get("email")
            password = form.data.get("password")
            user = authenticate(request, username=email, password=password)
        
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next')
                return redirect(next_url if next_url else "blogs-post-list")
            else:
                error = "Неверный email или пароль"
                return render(request, 'users/login.html', {'error': error, 'email': email})

class ProfileView(View):
    def get(self, request):
        form = UserForm(instance=request.user)
        user = get_object_or_404(User, pk=request.user.id)
        return render(request=request, template_name="users/profile.html", context={"page_title": "Профиль", "form": form, "user": user})
    def post(self, request):
        user = get_object_or_404(User, pk=request.user.id)
        form = UserForm(data=request.POST, files=request.FILES, instance=request.user)
        if form.is_valid():
            form.save()

            return redirect("users-profile")
        return render(request=request, template_name="users/profile.html", context={"page_title": "Профиль", "form": form, "user": user})

@require_POST
def logout(request):
    django_logout(request)
    return redirect('login')