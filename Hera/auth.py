from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        print(user)
        print(user.email)

        token['xx'] = user.email

        print(token)
        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    # print('-------')
    serializer_class = CustomTokenObtainPairSerializer
