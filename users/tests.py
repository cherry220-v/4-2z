from django.test import TestCase
from django.urls import reverse

from .models import User


class LoginTest(TestCase):
    def setUp(self):
        self.register_url = reverse("users-register")
        self.user = User.objects.create_user(
            username="test_user", email="test@user.f", password="notstrongpassword")
    
    def test_login(self):
        exp1 = self.client.login(email="test@user.f", password="notstrongpassword")
        exp2 = self.client.login(email="nottest@user.f", password="notstrongpassword")
        self.assertTrue(expr=exp1)
        self.assertFalse(expr=exp2)
        
def test_register(self):
    tryRegister1 = self.client.post(
        self.register_url,
        {
            "username": "AlexeyNavi",
            "email": "test@user.f2",
            "password": "1",
            "password_confirm": "1",
        },
    )
    self.assertEqual(tryRegister1.status_code, 302)

    tryRegister2 = self.client.post(
        self.register_url,
        {
            "username": "AlexeyNavi2",
            "email": "test@user.f2",
            "password": "1",
            "password_confirm": "1",
        },
    )
    self.assertEqual(tryRegister2.status_code, 200)
    self.assertFormError(
        tryRegister2,
        "form",
        "email",
        "Пользователь с таким Email уже зарегистрирован.",
    )

    tryRegister3 = self.client.post(
        self.register_url,
        {
            "username": "AlexeyNavi3",
            "email": "test@user.f3",
            "password": "1",
            "password_confirm": "12",
        },
    )
    self.assertEqual(tryRegister3.status_code, 200)
    self.assertFormError(tryRegister3, "form", "password", "Пароли не совпадают")

    tryRegister4 = self.client.post(
        self.register_url,
        {
            "username": "AlexeyNavi3",
            "email": "test@user.f4",
            "password": "1",
            "password_confirm": "1",
        },
    )
    tryRegister4 = self.client.post(
        self.register_url,
        {
            "username": "AlexeyNavi",
            "email": "test@user.f4",
            "password": "1",
            "password_confirm": "1",
        },
    )
    self.assertEqual(tryRegister4.status_code, 200)
    self.assertFormError(
        tryRegister4, "form", "username", "Это имя пользователя уже занято."
    )

    self.assertEqual(User.objects.count(), 2)