from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import SerialKey, DeviceInfo
import json

@csrf_exempt
def check_key(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        key = data.get('key')
        device_id = data.get('device_id')

        try:
            serial_key = SerialKey.objects.get(key=key)
            if serial_key.is_used:
                return JsonResponse({'status': 'error', 'message': 'Key already used'}, status=400)
            else:
                serial_key.is_used = True
                serial_key.save()
                DeviceInfo.objects.create(serial_key=serial_key, device_id=device_id)
                return JsonResponse({'status': 'success', 'message': 'Key activated'})
        except SerialKey.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid key'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)