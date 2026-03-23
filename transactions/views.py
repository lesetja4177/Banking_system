# transactions/views.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password, make_password
import time

from .models import Transfer
from .serializers import TransferSerializer
from .utils import generate_receipt  # handles Dropbox upload


class CreateTransferView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data.copy()  # copy to safely modify
        pin = data.pop("pin", None)  # remove pin before sending to serializer

        # -------------------- 1️⃣ Validate Amount --------------------
        amount = data.get("amount")
        if amount is None:
            return Response({"error": "Amount is required"}, status=400)
        try:
            amount = float(amount)
        except ValueError:
            return Response({"error": "Invalid amount"}, status=400)

        # -------------------- 2️⃣ Handle PIN --------------------
        if not user.transaction_pin:
            # First-time PIN creation
            if not pin:
                return Response({"error": "You must provide a PIN for first-time setup."}, status=400)
            if not pin.isdigit() or len(pin) != 6:
                return Response({"error": "PIN must be exactly 6 digits."}, status=400)
            user.transaction_pin = make_password(pin)
            user.save()
        else:
            # Existing PIN verification
            if not pin:
                return Response({"error": "Transaction PIN is required"}, status=400)
            if not check_password(pin, user.transaction_pin):
                return Response({"error": "Invalid transaction PIN"}, status=400)

        # -------------------- 3️⃣ Check restrictions & balance --------------------
        if getattr(user, "is_restricted", False):
            return Response({"error": "Account Restricted"}, status=403)
        if user.balance < amount:
            return Response({"error": "Insufficient balance"}, status=400)

        # -------------------- 4️⃣ Validate & save transfer --------------------
        serializer = TransferSerializer(data=data)
        if serializer.is_valid():
            transfer = serializer.save(user=user, status="Pending")

            # -------------------- 5️⃣ Simulate processing delay --------------------
            time.sleep(3)

            # -------------------- 6️⃣ Deduct balance --------------------
            user.balance -= transfer.amount
            user.save()

            # -------------------- 7️⃣ Mark transfer completed --------------------
            transfer.status = "Completed"
            transfer.save()

            # -------------------- 8️⃣ Generate receipt --------------------
            receipt_url = None
            try:
                receipt_url = generate_receipt(user, transfer)
            except Exception as e:
                print("Receipt generation/upload error:", str(e))

            # -------------------- 9️⃣ Return success --------------------
            return Response({
                "success": True,
                "message": "Transaction Successful",
                "transfer_id": transfer.id,
                "new_balance": user.balance,
                "receipt_url": receipt_url
            })

        # -------------------- 10️⃣ Serializer errors --------------------
        return Response(serializer.errors, status=400)