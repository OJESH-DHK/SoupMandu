from django.db import models

class PortionType(models.TextChoices):
    COUNTABLE = "COUNTABLE", "Countable (pieces)"
    PORTION = "PORTION", "Portion (S/M/L)"