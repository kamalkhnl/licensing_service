from django.contrib import admin
from .models import SerialKey, DeviceInfo

@admin.register(SerialKey)
class SerialKeyAdmin(admin.ModelAdmin):
    list_display = ('key', 'is_used', 'created_at')
    search_fields = ('key',)

@admin.register(DeviceInfo)
class DeviceInfoAdmin(admin.ModelAdmin):
    list_display = ('serial_key', 'device_id', 'activation_date')
    search_fields = ('serial_key__key', 'device_id')