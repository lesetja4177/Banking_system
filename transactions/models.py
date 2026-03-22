from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Transfer(models.Model):

    TRANSFER_TYPE = (
        ("LOCAL", "Local Transfer"),
        ("INTERNATIONAL", "International Transfer"),
        ("CRYPTO", "Crypto Transfer"),
    )

    CRYPTO_TYPE = (
        ("BTC", "Bitcoin"),
        ("USDT_ETH", "USDT (Ethereum)"),
        ("USDT_TRON", "USDT (Tron)"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    transfer_type = models.CharField(max_length=20, choices=TRANSFER_TYPE)

    bank_name = models.CharField(max_length=255, blank=True)
    account_number = models.CharField(max_length=50, blank=True)

    crypto_type = models.CharField(max_length=20, choices=CRYPTO_TYPE, blank=True)
    crypto_address = models.CharField(max_length=255, blank=True)

    status = models.CharField(max_length=20, default="Pending")

    otp = models.CharField(max_length=6, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.amount}"