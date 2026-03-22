from django.urls import path
from .views import CreateTransferView, SetPinView

urlpatterns = [
    # Endpoint to create/send a transfer
    path("create/", CreateTransferView.as_view(), name="create-transfer"),

    # Endpoint to create a 6-digit PIN
    path("set-pin/", SetPinView.as_view(), name="set-pin"),
]