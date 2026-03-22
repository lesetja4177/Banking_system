from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .views import (
    RegisterView,
    CustomLoginView,
    ProfileView,
    CreatePinView,
    VerifyPinView,
    TransactionListView
)

urlpatterns = [
    path('register/', csrf_exempt(RegisterView.as_view())),  # CSRF exempt
    path('login/', CustomLoginView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('set-pin/', CreatePinView.as_view()),
    path('verify-pin/', VerifyPinView.as_view()),
    path('transactions/', TransactionListView.as_view()),
]