from django.urls import path

from users.views import ProfileView, ConfirmUser

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('confirm/', ConfirmUser.as_view(), name='confirm_user'),
    ]
