# transactions/views.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password
import time
import os
from django.conf import settings
from fpdf import FPDF

from .models import Transfer
from .serializers import TransferSerializer

# ---------------------- UTILITY: GENERATE RECEIPT ----------------------
def generate_receipt(user, transfer):
    """
    Generate PDF receipt locally on Railway and return URL
    """
    receipt_folder = os.path.join(settings.MEDIA_ROOT, "receipts")
    os.makedirs(receipt_folder, exist_ok=True)

    filename = f"receipt_{transfer.id}.pdf"
    file_path = os.path.join(receipt_folder, filename)

    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="Transaction Receipt", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"User: {user.username}", ln=True)
    pdf.cell(200, 10, txt=f"Amount: ${transfer.amount}", ln=True)
    pdf.cell(200, 10, txt=f"Status: {transfer.status}", ln=True)
    pdf.cell(200, 10, txt=f"Transfer Type: {transfer.transfer_type}", ln=True)
    pdf.cell(200, 10, txt=f"Transfer ID: {transfer.id}", ln=True)
    pdf.cell(200, 10, txt=f"Date: {transfer.created_at.strftime('%Y-%m-%d %H:%M:%S')}", ln=True)

    pdf.output(file_path)

    # Return direct URL
    receipt_url = f"{settings.BASE_URL}{settings.MEDIA_URL}receipts/{filename}"
    return receipt_url


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

            # Simulate processing delay
            time.sleep(3)

            # Deduct balance
            user.balance -= transfer.amount
            user.save()

            # Mark transfer completed
            transfer.status = "Completed"
            transfer.save()

            # Generate receipt
            receipt_url = None
            try:
                receipt_url = generate_receipt(user, transfer)
            except Exception as e:
                print("Receipt generation error:", str(e))

            return Response({
                "success": True,
                "message": "Transaction Successful",
                "transfer_id": transfer.id,
                "new_balance": user.balance,
                "receipt_url": receipt_url
            })

        return Response(serializer.errors, status=400)