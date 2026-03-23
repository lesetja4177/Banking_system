from django.urls import path
from .views import CreateTransferView

urlpatterns = [
    # Endpoint to create/send a transfer
    path("create/", CreateTransferView.as_view(), name="create-transfer"),
]