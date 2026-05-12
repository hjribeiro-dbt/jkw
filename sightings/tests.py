from decimal import Decimal
from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import JKWSighting


class JKWSightingsAPITests(APITestCase):
    def setUp(self):
        self.url = reverse("list-create-sightings")

    def test_get_empty_list_returns_200_and_empty_array(self):
        # Ensure DB is empty
        JKWSighting.objects.all().delete()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 0)

    def test_get_list_returns_ordered_data_and_schema(self):
        # Create two records with controlled timestamps to verify ordering
        s1 = JKWSighting.objects.create(
            latitude=Decimal("12.345678"),
            longitude=Decimal("98.765432"),
            description="First",
        )
        s2 = JKWSighting.objects.create(
            latitude=Decimal("-45.000000"),
            longitude=Decimal("179.999999"),
            description="Second",
        )

        # Manually adjust created_at to ensure deterministic ordering
        older = timezone.now() - timedelta(days=1)
        newer = timezone.now()
        JKWSighting.objects.filter(pk=s1.pk).update(created_at=older)
        JKWSighting.objects.filter(pk=s2.pk).update(created_at=newer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 2)

        # Expect s2 (newer) first due to '-created_at' ordering
        first, second = response.data[0], response.data[1]

        # Verify schema keys
        expected_keys = {"id", "latitude", "longitude", "description", "created_at"}
        self.assertEqual(set(first.keys()), expected_keys)
        self.assertEqual(set(second.keys()), expected_keys)

        # Verify values for first item (s2)
        s2_refreshed = JKWSighting.objects.get(pk=s2.pk)
        self.assertEqual(first["id"], s2_refreshed.id)
        # DRF commonly serializes Decimals as strings by default
        self.assertEqual(first["latitude"], str(s2_refreshed.latitude))
        self.assertEqual(first["longitude"], str(s2_refreshed.longitude))
        self.assertEqual(first["description"], s2_refreshed.description)
        self.assertIsInstance(first["created_at"], str)

        # Verify second item corresponds to s1 (older)
        s1_refreshed = JKWSighting.objects.get(pk=s1.pk)
        self.assertEqual(second["id"], s1_refreshed.id)
        self.assertEqual(second["latitude"], str(s1_refreshed.latitude))
        self.assertEqual(second["longitude"], str(s1_refreshed.longitude))
        self.assertEqual(second["description"], s1_refreshed.description)
        self.assertIsInstance(second["created_at"], str)

    def test_post_valid_creates_record_and_returns_201(self):
        payload = {
            "latitude": "10.123456",
            "longitude": "-20.654321",
            "description": "A brand new sighting",
        }
        before = JKWSighting.objects.count()
        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(JKWSighting.objects.count(), before + 1)

        # Verify response schema and values
        expected_keys = {"id", "latitude", "longitude", "description", "created_at"}
        self.assertEqual(set(response.data.keys()), expected_keys)
        obj = JKWSighting.objects.order_by("-id").first()
        self.assertEqual(response.data["id"], obj.id)
        self.assertEqual(response.data["latitude"], str(obj.latitude))
        self.assertEqual(response.data["longitude"], str(obj.longitude))
        self.assertEqual(response.data["description"], obj.description)
        self.assertIsInstance(response.data["created_at"], str)

    def test_post_missing_latitude_returns_400(self):
        payload = {
            "longitude": "0.000000",
            "description": "no lat",
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("latitude", response.data)

    def test_post_missing_longitude_returns_400(self):
        payload = {
            "latitude": "0.000000",
            "description": "no lon",
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("longitude", response.data)

    def test_post_invalid_latitude_range_returns_400_with_message(self):
        payload = {"latitude": "90.000001", "longitude": "0.000000"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("latitude", response.data)
        self.assertIn("Latitude must be between -90 and 90.", response.data["latitude"]) 

    def test_post_invalid_longitude_range_returns_400_with_message(self):
        payload = {"latitude": "0.000000", "longitude": "180.000001"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("longitude", response.data)
        self.assertIn("Longitude must be between -180 and 180.", response.data["longitude"]) 

    def test_post_allows_blank_description(self):
        payload = {"latitude": "1.000000", "longitude": "1.000000", "description": ""}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        obj = JKWSighting.objects.get(pk=response.data["id"])
        self.assertEqual(obj.description, "")
        self.assertEqual(response.data["description"], "")

    def test_post_read_only_fields_are_ignored(self):
        # Client attempts to set id and created_at; these should be ignored
        payload = {
            "latitude": "2.000000",
            "longitude": "3.000000",
            "description": "tries to set read-only",
            "id": 99999,
            "created_at": "1999-01-01T00:00:00Z",
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        obj = JKWSighting.objects.get(pk=response.data["id"])
        # Ensure the id is not the client-sent one
        self.assertNotEqual(obj.id, 99999)
        # Ensure created_at is not the client-sent timestamp
        self.assertNotEqual(response.data["created_at"], "1999-01-01T00:00:00Z")
