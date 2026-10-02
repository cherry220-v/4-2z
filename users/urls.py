from django.urls import path
from .views import LoginView, RegisterView, ProfileView, logout

urlpatterns = [
    path("login/", LoginView.as_view(),       name="users-login"),
    path("register/", RegisterView.as_view(), name="users-register"),
    path("profile/", ProfileView.as_view(),   name="users-profile"),
    path("logout/", logout,                   name="users-logout"),
]