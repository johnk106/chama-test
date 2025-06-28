from django.shortcuts import render, redirect
from django.http import HttpResponse
from .services.auth_service import AuthManager
from .services.password_service import PasswordService
from .services.firebase_service import FirebaseService
from .services.account_service import AccountService

# Auth views

def Login(request): return AuthManager.login_view(request)

def login_token(request): return AuthManager.initiate_token_login(request)

def login_otp(request): return AuthManager.token_login(request)

def Sign_Up(request): return AuthManager.signup(request)

def verify_otp(request): return AuthManager.complete_signup(request)

def Sign_Up2(request): return AuthManager.signup_step2(request)

def Logout(request): return AuthManager.logout_view(request)

# Password reset views

def forget_password(request): return PasswordService.forget_password(request)

def reset_password(request): return PasswordService.reset_password(request)

def update_password(request): return PasswordService.update_password(request)

# Firebase JS view

def showFirebaseJS(request): return FirebaseService.serve_firebase_js(request)

# Account deletion view

def delete_account(request): return AccountService.delete_account(request)