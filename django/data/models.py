from django.db import models


# Create your models here.
class EOD(models.Model):
    id = models.AutoField(primary_key=True)
    symbol = models.CharField(max_length=20)
    datetime = models.DateField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.BigIntegerField()
    oi = models.BigIntegerField(null=True, blank=True)

    class Meta:
        db_table = "tfw_eod"
        indexes = [
            models.Index(fields=["symbol", "datetime"]),
        ]
        managed = True
