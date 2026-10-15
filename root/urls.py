"""
URL configuration for root project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from app.views import ProductListAPIView, ForgotPasswordView, ConfirmPasswordView, ResetPasswordView, RegisterView, \
    VerifyEmailView, ResendCodeView

schema_view = get_schema_view(
    openapi.Info(
        title="BirZumda API",
        default_version='v1',
        description="Azob",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('product/', ProductListAPIView.as_view(), name='product'),
    path("user/register/", RegisterView.as_view()),
    path("user/verify-email/", VerifyEmailView.as_view()),
    path("user/resend-code/", ResendCodeView.as_view()),
    path("user/login/", TokenObtainPairView.as_view()),
    path("user/refresh/", TokenRefreshView.as_view()),
    path("user/logout/", LogoutView.as_view()),
    path("forgot/forgot-password/", ForgotPasswordView.as_view()),
    path("forgot/confirm-password/", ConfirmPasswordView.as_view()),
    path("forgot/reset-password/", ResetPasswordView.as_view()),
]
