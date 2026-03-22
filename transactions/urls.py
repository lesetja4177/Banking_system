from django.urls import path
from .views import CreateTransferView, VerifyTransferView

urlpatterns = [
    path("create/", CreateTransferView.as_view()),
    path("verify/", VerifyTransferView.as_view()),
    path('accounts/set-pin/', SetPinView.as_view()),
]