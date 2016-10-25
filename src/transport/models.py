from django.db import models
from transport.constants import TRANSPORT_MODES


class Line(models.Model):
    """
    A transport line
    """
    mode = models.CharField(max_length=20, choices=TRANSPORT_MODES)
    operator = models.CharField(max_length=250, null=True, blank=True)
    name = models.CharField(max_length=250)
    full_name = models.TextField()

    # Api ids
    itinisere_id = models.IntegerField(unique=True)
    metro_id = models.CharField(max_length=250, null=True, blank=True)

    class Meta:
        unique_together = (
            ('mode', 'name'),
        )

    def __str__(self):
        return '{} {}'.format(self.mode, self.name)

class Direction(models.Model):
    """
    A direction for a transport line
    """
    line = models.ForeignKey(Line, related_name='directions')
    itinisere_id = models.IntegerField() # 1|2
    name = models.CharField(max_length=250)

    class Meta:
        unique_together = (
            ('line', 'itinisere_id'),
        )
