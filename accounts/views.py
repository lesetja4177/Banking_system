from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import (
    RegisterSerializer,
    TransactionSerializer,
    CustomLoginSerializer,
    UserSerializer,
    CreatePinSerializer,
    VerifyPinSerializer
)
from transactions.models import Transfer

class TransactionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = Transfer.objects.filter(user=request.user).order_by('-created_at')
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    # GET profile
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    # UPDATE profile
    def patch(self, request):
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


@csrf_exempt
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomLoginSerializer


class CreatePinView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreatePinSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"message": "PIN created successfully"})
        return Response(serializer.errors, status=400)


class VerifyPinView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = VerifyPinSerializer(
            data=request.data,
            context={"user": request.user}
        )
        if serializer.is_valid():
            return Response({"message": "PIN verified"})
        return Response(serializer.errors, status=400)