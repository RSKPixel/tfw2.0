from django.db import models


# Create your models here.
class EOD(models.Model):
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

        constraints = [
            models.UniqueConstraint(
                fields=["symbol", "datetime"], name="unique_symbol_datetime_v2"
            )
        ]
        managed = True


class IData15m(models.Model):
    symbol = models.CharField(max_length=20)
    datetime = models.DateTimeField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.BigIntegerField()

    class Meta:
        db_table = "tfw_idata_15m"

        constraints = [
            models.UniqueConstraint(
                fields=["symbol", "datetime"], name="unique_symbol_datetime_15m"
            )
        ]
        managed = True


class IData75m(models.Model):
    symbol = models.CharField(max_length=20)
    datetime = models.DateTimeField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.BigIntegerField()

    class Meta:
        db_table = "tfw_idata_75m"

        constraints = [
            models.UniqueConstraint(
                fields=["symbol", "datetime"], name="unique_symbol_datetime_75m"
            )
        ]
        managed = True
