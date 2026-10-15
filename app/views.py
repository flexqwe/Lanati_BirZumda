from datetime import timedelta, timezone

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import permissions, generics
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from app import models
from app.serializers import ProductModelSerializer, RegisterSerializer, VerifyEmailSerializer, ResendCodeSerializer, \
    ResetPasswordSerializer, ConfirmPasswordSerializer, ForgotPasswordSerializer
from .filters import ProductFilter
from .models import EmailCode, User
from .pagination import ProductPagination


class ProductListAPIView(ListAPIView):
    serializer_class = ProductModelSerializer
    queryset = models.Product.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ProductFilter
    search_fields = ['title', 'category__title']
    pagination_class = ProductPagination
    permission_classes = [permissions.AllowAny]


from .services import send_verification_code, confirm_code, finish_code
from .services.pre_token import make_pre_token, get_user


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        send_verification_code(user)
        return Response(
            {"email": user.email, "pre_token": make_pre_token(user.id)},
            status=201,
        )


class VerifyEmailView(generics.GenericAPIView):
    serializer_class = VerifyEmailSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = get_user(data["pre_token"])
        confirm_code(user, data["code"])     # 1. tasdiqla
        user.is_active = True                # 2. ishingni qil
        user.save()
        finish_code(user)                    # 3. yop
        return Response(
            {"detail": "Email tasdiqlandi. Endi login qiling."}
        )


RESEND_INTERVAL = timedelta(seconds=60)


class ResendCodeView(generics.GenericAPIView):
    serializer_class = ResendCodeSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_user(serializer.validated_data["pre_token"])

        record = EmailCode.objects.filter(user=user).first()
        now = timezone.now()
        if record and now - record.created_at < RESEND_INTERVAL:
            return Response(
                {"detail": "1 daqiqada faqat 1 marta"}, status=429
            )

        send_verification_code(user)
        # yangi pre_token — yana 30 daqiqa
        return Response({"pre_token": make_pre_token(user.id)})


class ForgotPasswordView(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        user = User.objects.filter(email=email, is_active=True).first()
        if user:
            send_verification_code(user)   # register'dagi funksiya

        # email yo'q bo'lsa ham javob bir xil (user_id=0)
        user_id = user.id if user else 0
        return Response({"pre_token": make_pre_token(user_id)})


class ConfirmPasswordView(generics.GenericAPIView):
    serializer_class = ConfirmPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = get_user(data["pre_token"])
        confirm_code(user, data["code"])
        return Response({"detail": "Kod to'g'ri. Yangi parol kiriting."})


class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = get_user(data["pre_token"])
        finish_code(user)          # kod tasdiqlanmagan bo'lsa — 400
        user.set_password(data["new_password"])
        user.save()
        return Response({"detail": "Parol yangilandi."})