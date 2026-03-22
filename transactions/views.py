from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password, make_password
import time

from .models import Transfer
from .serializers import TransferSerializer
from .utils import generate_receipt


# ---------------------- SET / CREATE 6-DIGIT PIN ----------------------
class SetPinView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        pin = request.data.get("pin")

        if not pin:
            return Response({"error": "PIN is required"}, status=400)
        if len(str(pin)) != 6 or not str(pin).isdigit():
            return Response({"error": "PIN must be exactly 6 digits"}, status=400)

        user.transaction_pin = make_password(pin)
        user.save()

        return Response({"message": "PIN created successfully"})


# ---------------------- CREATE TRANSFER (PIN CHECK + PROCESSING) ----------------------
class CreateTransferView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        amount = request.data.get("amount")
        pin = request.data.get("pin")

        # Validate amount
        if not amount:
            return Response({"error": "Amount is required"}, status=400)
        try:
            amount = float(amount)
        except ValueError:
            return Response({"error": "Invalid amount"}, status=400)

        # Check if user has PIN
        if not getattr(user, "transaction_pin", None):
            return Response({"error": "No transaction PIN set. Please create one first."}, status=400)

        # Validate PIN
        if not pin:
            return Response({"error": "Transaction PIN is required"}, status=400)
        if not check_password(pin, user.transaction_pin):
            return Response({"error": "Invalid transaction PIN"}, status=400)

        # Check restrictions and balance
        if getattr(user, "is_restricted", False):
            return Response({"error": "Account Restricted"}, status=403)
        if user.balance < amount:
            return Response({"error": "Insufficient balance"}, status=400)

        # Save transfer as Pending
        serializer = TransferSerializer(data=request.data)
        if serializer.is_valid():
            transfer = serializer.save(user=user, status="Pending")

            # Simulate 3-second processing delay
            time.sleep(3)

            # Deduct balance
            user.balance -= transfer.amount
            user.save()

            # Mark transfer completed
            transfer.status = "Completed"
            transfer.save()

            # Optionally generate PDF receipt
            try:
                generate_receipt(user, transfer)
            except Exception as e:
                print("Receipt generation error:", str(e))

            return Response({
                "success": True,
                "message": "Transaction Successful",
                "transfer_id": transfer.id,
                "new_balance": user.balance
            })

        return Response(serializer.errors, status=400)