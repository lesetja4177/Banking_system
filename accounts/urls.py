from django.urls import path
from .views import RegisterView,TransactionListView
from .views import RegisterView, CustomLoginView
from .views import ProfileView
from .views import CreatePinView, VerifyPinView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', CustomLoginView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('create-pin/', CreatePinView.as_view()),
    path('verify-pin/', VerifyPinView.as_view()),
    path('transactions/', TransactionListView.as_view()),
]