from django.db import models

# Create your models here.
from django.db import models

class MelodicTransition(models.Model):
    current_note = models.CharField(max_length=10, db_index=True)
    next_note = models.CharField(max_length=10)
    pair_count = models.IntegerField()
    total_occurrences = models.IntegerField()
    probability = models.FloatField()

    def __str__(self):
        return f"{self.current_note} to {self.next_note}"