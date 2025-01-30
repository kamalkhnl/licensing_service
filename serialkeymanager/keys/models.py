from django.db import models

class SerialKey(models.Model):
    key = models.CharField(max_length=16, unique=True)  # 16-digit serial key
    is_used = models.BooleanField(default=False)  # Track if the key is used
    created_at = models.DateTimeField(auto_now_add=True)  # When the key was generated

    def __str__(self):
        return self.key

class DeviceInfo(models.Model):
    serial_key = models.OneToOneField(SerialKey, on_delete=models.CASCADE, related_name='device_info')
    device_id = models.CharField(max_length=100)  # Unique device identifier
    activation_date = models.DateTimeField(auto_now_add=True)  # When the key was activated

    def __str__(self):
        return f"{self.serial_key.key} - {self.device_id}"