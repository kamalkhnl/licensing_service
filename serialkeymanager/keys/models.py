from django.core.validators import RegexValidator
from django.db import models


serial_key_validator = RegexValidator(
    regex=r"^[A-Z0-9]{16}$",
    message="Serial keys must be 16 uppercase letters or digits.",
)


class SerialKey(models.Model):
    key = models.CharField(
        max_length=16,
        unique=True,
        validators=[serial_key_validator],
        help_text="16-character uppercase alphanumeric serial key.",
    )
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.key


class DeviceInfo(models.Model):
    serial_key = models.OneToOneField(
        SerialKey,
        on_delete=models.CASCADE,
        related_name="device_info",
    )
    device_id = models.CharField(max_length=100, unique=True)
    activation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-activation_date"]

    def __str__(self):
        return f"{self.serial_key.key} - {self.device_id}"
