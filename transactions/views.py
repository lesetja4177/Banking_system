# transactions/views.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password
import time

from .models import Transfer
from .serializers import TransferSerializer
from .utils import generate_receipt  # handles Dropbox upload


# ---------------------- CREATE TRANSFER (PIN CHECK + PROCESSING) ----------------------
class CreateTransferView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data.copy()  # ✅ copy to safely modify
        pin = data.pop("pin", None)  # 🔥 remove PIN before serializer

        # -------------------- 1️⃣ Validate Amount --------------------
        amount = data.get("amount")
        if not amount:
            return Response({"error": "Amount is required"}, status=400)
        try:
            amount = float(amount)
        except ValueError:
            return Response({"error": "Invalid amount"}, status=400)

        # -------------------- 2️⃣ Validate PIN --------------------
        if not getattr(user, "transaction_pin", None):
            return Response({"error": "No transaction PIN set. Please create one first."}, status=400)

        if not pin:
            return Response({"error": "Transaction PIN is required"}, status=400)
        if not check_password(pin, user.transaction_pin):
            return Response({"error": "Invalid transaction PIN"}, status=400)

        # -------------------- 3️⃣ Check Restrictions & Balance --------------------
        if getattr(user, "is_restricted", False):
            return Response({"error": "Account Restricted"}, status=403)
        if user.balance < amount:
            return Response({"error": "Insufficient balance"}, status=400)

        # -------------------- 4️⃣ Validate & Save Transfer --------------------
        serializer = TransferSerializer(data=data)
        if serializer.is_valid():
            transfer = serializer.save(user=user, status="Pending")

            # -------------------- 5️⃣ Simulate Processing Delay --------------------
            time.sleep(3)

            # -------------------- 6️⃣ Deduct Balance --------------------
            user.balance -= transfer.amount
            user.save()

            # -------------------- 7️⃣ Mark Transfer Completed --------------------
            transfer.status = "Completed"
            transfer.save()

            # -------------------- 8️⃣ Generate Receipt --------------------
            receipt_url = None
            try:
                receipt_url = generate_receipt(user, transfer)
            except Exception as e:
                print("Receipt generation/upload error:", str(e))

            # -------------------- 9️⃣ Response --------------------
            return Response({
                "success": True,
                "message": "Transaction Successful",
                "transfer_id": transfer.id,
                "new_balance": user.balance,
                "receipt_url": receipt_url
            })

        # -------------------- 10️⃣ Serializer Errors --------------------
        return Response(serializer.errors, status=400)