import json
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.urls import reverse

from .models import DeviceInfo, SerialKey


class KeyApiTests(TestCase):
    def setUp(self):
        self.serial_key = SerialKey.objects.create(key="ABCDEF1234567890")
        self.assign_url = reverse("assign_key")
        self.check_url = reverse("check_key")

    def post_json(self, url, payload):
        return self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
        )

    def test_assign_key_activates_available_key(self):
        response = self.post_json(
            self.assign_url,
            {"key": "abcdef1234567890", "device_id": "device-1"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")
        self.serial_key.refresh_from_db()
        self.assertTrue(self.serial_key.is_used)
        self.assertEqual(self.serial_key.device_info.device_id, "device-1")

    def test_assign_key_is_idempotent_for_same_device(self):
        self.post_json(self.assign_url, {"key": self.serial_key.key, "device_id": "device-1"})

        response = self.post_json(
            self.assign_url,
            {"key": self.serial_key.key, "device_id": "device-1"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(DeviceInfo.objects.count(), 1)

    def test_assign_key_rejects_different_device_for_used_key(self):
        self.post_json(self.assign_url, {"key": self.serial_key.key, "device_id": "device-1"})

        response = self.post_json(
            self.assign_url,
            {"key": self.serial_key.key, "device_id": "device-2"},
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["status"], "error")

    def test_check_key_reports_available_key_without_activating_it(self):
        response = self.post_json(
            self.check_url,
            {"key": self.serial_key.key, "device_id": "device-1"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["valid"], True)
        self.assertEqual(response.json()["activated"], False)
        self.serial_key.refresh_from_db()
        self.assertFalse(self.serial_key.is_used)

    def test_check_key_accepts_assigned_device(self):
        self.post_json(self.assign_url, {"key": self.serial_key.key, "device_id": "device-1"})

        response = self.post_json(
            self.check_url,
            {"key": self.serial_key.key, "device_id": "device-1"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["valid"], True)
        self.assertEqual(response.json()["activated"], True)

    def test_check_key_rejects_different_device(self):
        self.post_json(self.assign_url, {"key": self.serial_key.key, "device_id": "device-1"})

        response = self.post_json(
            self.check_url,
            {"key": self.serial_key.key, "device_id": "device-2"},
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["valid"], False)

    def test_invalid_json_returns_bad_request(self):
        response = self.client.post(
            self.assign_url,
            data="not-json",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["status"], "error")

    def test_missing_fields_return_bad_request(self):
        response = self.post_json(self.assign_url, {"key": self.serial_key.key})

        self.assertEqual(response.status_code, 400)
        self.assertIn("device_id", response.json()["message"])


class GenerateKeysCommandTests(TestCase):
    def test_generate_keys_creates_requested_number_of_keys(self):
        output = StringIO()

        call_command("generate_keys", 3, stdout=output)

        self.assertEqual(SerialKey.objects.count(), 3)
        self.assertIn("Successfully generated 3 keys", output.getvalue())
        self.assertTrue(all(len(key.key) == 16 for key in SerialKey.objects.all()))

    def test_generate_keys_requires_positive_count(self):
        with self.assertRaises(CommandError):
            call_command("generate_keys", 0)

    def test_generate_keys_retries_duplicate_keys(self):
        SerialKey.objects.create(key="AAAAAAAAAAAAAAAA")
        choices = ["A"] * 16 + ["B"] * 16

        with patch("keys.management.commands.generate_keys.secrets.choice", side_effect=choices):
            call_command("generate_keys", 1)

        self.assertTrue(SerialKey.objects.filter(key="BBBBBBBBBBBBBBBB").exists())
