import random
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.mail import send_mail, EmailMessage
from django.contrib.auth.hashers import check_password, make_password

from .models import Transfer
from .serializers import TransferSerializer
from .utils import generate_receipt


# ============================================================
# SET / CREATE 6-DIGIT TRANSACTION PIN
# ============================================================
class SetPinView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        pin = request.data.get("pin")

        if not pin:
            return Response({"error": "PIN is required"}, status=400)

        # Require exactly 6 digits
        if len(str(pin)) != 6 or not str(pin).isdigit():
            return Response({"error": "PIN must be exactly 6 digits"}, status=400)

        # Save hashed PIN
        user.transaction_pin = make_password(pin)
        user.save()

        return Response({"message": "PIN created successfully"})


# ============================================================
# CREATE TRANSFER (PIN + OTP)
# ============================================================
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

        # Check restriction
        if getattr(user, "is_restricted", False):
            return Response({"error": "Account Restricted"}, status=403)

        # Check PIN exists
        if not getattr(user, "transaction_pin", None) or str(user.transaction_pin).strip() == "":
            return Response({"error": "No transaction PIN set"}, status=400)

        # Validate PIN input
        if not pin:
            return Response({"error": "Transaction PIN is required"}, status=400)
        if not check_password(pin, user.transaction_pin):
            return Response({"error": "Invalid transaction PIN"}, status=400)

        # Check balance
        if user.balance < amount:
            return Response({"error": "Insufficient balance"}, status=400)

        # Generate OTP
        otp = str(random.randint(100000, 999999))

        # Save transfer
        serializer = TransferSerializer(data=request.data)
        if serializer.is_valid():
            transfer = serializer.save(user=user, otp=otp)

            # Send OTP email
            send_mail(
                "Transaction OTP",
                f"Your OTP is {otp}",
                "noreply@bank.com",
                [user.email],
                fail_silently=False,
            )

            return Response({
                "message": "OTP sent to your email",
                "transfer_id": transfer.id
            })

        return Response(serializer.errors, status=400)


# ============================================================
# VERIFY OTP + COMPLETE TRANSFER + SEND RECEIPT
# ============================================================
class VerifyTransferView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        transfer_id = request.data.get("transfer_id")
        input_otp = request.data.get("otp")

        # Validate input
        if not transfer_id or not input_otp:
            return Response({"error": "transfer_id and otp are required"}, status=400)

        try:
            transfer = Transfer.objects.get(id=transfer_id, user=user)
        except Transfer.DoesNotExist:
            return Response({"error": "Transfer not found"}, status=404)

        # Check restriction
        if getattr(user, "is_restricted", False):
            return Response({"error": "Account Restricted"}, status=403)

        # Verify OTP
        if transfer.otp != input_otp:
            return Response({"error": "Invalid OTP"}, status=400)

        # Check balance again
        if user.balance < transfer.amount:
            return Response({"error": "Insufficient balance"}, status=400)

        # Deduct balance
        user.balance -= transfer.amount
        user.save()

        # Update transfer
        transfer.status = "Completed"
        transfer.otp = None
        transfer.save()

        # Generate PDF receipt
        try:
            file_path = generate_receipt(user, transfer)
            email = EmailMessage(
                subject="Transaction Successful",
                body="Your transaction was successful. Receipt attached.",
                from_email="noreply@bank.com",
                to=[user.email],
            )
            email.attach_file(file_path)
            email.send()
        except Exception as e:
            print("Email/PDF Error:", str(e))

        return Response({
            "message": "Transaction successful. Receipt sent to email"
        })