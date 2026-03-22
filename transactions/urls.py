from django.urls import path
from .views import CreateTransferView, VerifyTransferView, SetPinView

urlpatterns = [
    path("create/", CreateTransferView.as_view()),
    path("verify/", VerifyTransferView.as_view()),
    path("set-pin/", SetPinView.as_view()),
]