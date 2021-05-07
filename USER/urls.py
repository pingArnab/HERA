from django.urls import path
from . import views
from rest_framework_simplejwt import views as jwt_views
from . import auth


urlpatterns = [

    path('token/', auth.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', jwt_views.TokenVerifyView.as_view(), name='token_verify'),

    path('recommendation/', views.Recommendation.as_view()),
    path('wishlist/', views.Wishlist.as_view()),

]
