# transactions/views.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password
from django.conf import settings
from django.utils import timezone
from fpdf import FPDF
import os

from .models import Transfer
from .serializers import TransferSerializer

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

            # Deduct balance
            user.balance -= transfer.amount
            user.save()

            # Mark transfer completed
            transfer.status = "Completed"
            transfer.save()

            # Generate PDF receipt
            receipt_url = None
            try:
                receipt_url = self.generate_receipt(user, transfer)
            except Exception as e:
                print("Receipt generation error:", e)

            return Response({
                "success": True,
                "message": "Transaction Successful",
                "transfer_id": transfer.id,
                "new_balance": user.balance,
                "receipt_url": receipt_url
            })

        return Response(serializer.errors, status=400)

    # ---------------------- RECEIPT GENERATION ----------------------
    def generate_receipt(self, user, transfer):
        # Ensure receipts folder exists
        receipt_dir = os.path.join(settings.MEDIA_ROOT, "receipts")
        os.makedirs(receipt_dir, exist_ok=True)

        filename = f"receipt_{transfer.id}.pdf"
        filepath = os.path.join(receipt_dir, filename)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "Bank Transfer Receipt", ln=True, align="C")
        pdf.ln(10)
        pdf.set_font("Helvetica", "", 12)
        pdf.cell(0, 10, f"Transaction ID: {transfer.id}", ln=True)
        pdf.cell(0, 10, f"Date: {timezone.localtime(transfer.created_at).strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
        pdf.cell(0, 10, f"User: {user.username}", ln=True)
        pdf.cell(0, 10, f"Amount: ${transfer.amount:,.2f}", ln=True)
        pdf.cell(0, 10, f"Type: {transfer.transfer_type}", ln=True)
        pdf.cell(0, 10, f"Status: {transfer.status}", ln=True)

        pdf.output(filepath)

        # Return full URL
        base_url = getattr(settings, "BASE_URL", "")
        return f"{base_url}{settings.MEDIA_URL}receipts/{filename}"