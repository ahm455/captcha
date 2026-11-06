import uuid
from django.db import models

class Challenge(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    answer = models.CharField(max_length=16)
    image_png = models.BinaryField()
    created_at = models.DateTimeField(auto_now_add=True)

class AttemptLog(models.Model):
    challenge_type = models.CharField(max_length=40) 
    method = models.CharField(max_length=40)          
    success = models.BooleanField()
    reason = models.CharField(max_length=60, blank=True)
    time_ms = models.FloatField(default=0)
    cost_usd = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

class UsedToken(models.Model):
    fingerprint = models.CharField(max_length=64, unique=True)
    provider = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)