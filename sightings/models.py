from django.db import models


class JKWSighting(models.Model):
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"JKW sighting at {self.latitude}, {self.longitude}"

    class Meta:
        db_table = "jkw_sightings"