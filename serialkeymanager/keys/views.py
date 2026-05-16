import json

from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import DeviceInfo, SerialKey


REQUIRED_FIELDS = ("key", "device_id")


def _error_response(message, status=400, **extra):
    payload = {"status": "error", "message": message}
    payload.update(extra)
    return JsonResponse(payload, status=status)


def _success_response(message, **extra):
    payload = {"status": "success", "message": message}
    payload.update(extra)
    return JsonResponse(payload)


def _parse_json_body(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, _error_response("Request body must be valid JSON")

    if not isinstance(payload, dict):
        return None, _error_response("Request body must be a JSON object")

    missing_fields = [field for field in REQUIRED_FIELDS if not payload.get(field)]
    if missing_fields:
        return None, _error_response(
            "Missing required field(s): " + ", ".join(missing_fields)
        )

    key = str(payload["key"]).strip().upper()
    device_id = str(payload["device_id"]).strip()

    if not key or not device_id:
        return None, _error_response("Key and device_id cannot be blank")

    return {"key": key, "device_id": device_id}, None


@csrf_exempt
@require_POST
def assign_key(request):
    payload, error = _parse_json_body(request)
    if error:
        return error

    try:
        with transaction.atomic():
            serial_key = SerialKey.objects.select_for_update().get(key=payload["key"])

            if serial_key.is_used:
                device_info = getattr(serial_key, "device_info", None)
                if device_info and device_info.device_id == payload["device_id"]:
                    return _success_response("Key already activated for this device")
                return _error_response("Key already used", status=409)

            DeviceInfo.objects.create(
                serial_key=serial_key,
                device_id=payload["device_id"],
            )
            serial_key.is_used = True
            serial_key.save(update_fields=["is_used"])
    except SerialKey.DoesNotExist:
        return _error_response("Invalid key", status=404)
    except IntegrityError:
        return _error_response("Device is already assigned to another key", status=409)

    return _success_response("Key activated")


@csrf_exempt
@require_POST
def check_key(request):
    payload, error = _parse_json_body(request)
    if error:
        return error

    try:
        serial_key = SerialKey.objects.select_related("device_info").get(key=payload["key"])
    except SerialKey.DoesNotExist:
        return _error_response("Invalid key", status=404, valid=False)

    if not serial_key.is_used:
        return _success_response("Key is valid and available", valid=True, activated=False)

    device_info = getattr(serial_key, "device_info", None)
    if device_info and device_info.device_id == payload["device_id"]:
        return _success_response("Key is valid for this device", valid=True, activated=True)

    return _error_response("Key is assigned to a different device", status=403, valid=False)
