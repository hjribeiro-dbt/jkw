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
