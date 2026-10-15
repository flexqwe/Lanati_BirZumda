from django.contrib.auth import get_user_model
from django.core import signing
from rest_framework.serializers import ValidationError

User = get_user_model()
SALT = "pre-token"
ERROR = "pre_token yaroqsiz yoki muddati tugagan"


def make_pre_token(user_id):
    # SECRET_KEY bilan imzolanadi — soxtalab bo'lmaydi
    return signing.dumps({"user_id": user_id}, salt=SALT)


def get_user(pre_token):
    try:
        data = signing.loads(pre_token, salt=SALT, max_age=1800)
        user_id = data["user_id"]            # 30 daqiqa yashaydi
    except signing.BadSignature:
        user_id = None

    user = User.objects.filter(id=user_id).first()
    if user is None:
        raise ValidationError({"detail": ERROR})
    return user