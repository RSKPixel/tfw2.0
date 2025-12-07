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


# instrument_token,exchange_token,tradingsymbol,name,last_price,expiry,strike,tick_size,lot_size,instrument_type,segment,exchange


class Instruments(models.Model):
    instrument_token = models.BigIntegerField(primary_key=True)
    exchange_token = models.BigIntegerField()
    tradingsymbol = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    last_price = models.FloatField()
    expiry = models.DateField(null=True, blank=True)
    strike = models.FloatField(null=True, blank=True)
    tick_size = models.FloatField()
    lot_size = models.IntegerField()
    instrument_type = models.CharField(max_length=10)
    segment = models.CharField(max_length=20)
    exchange = models.CharField(max_length=10)

    class Meta:
        db_table = "tfw_instruments"
        constraints = [
            models.UniqueConstraint(
                fields=["tradingsymbol", "exchange"],
                name="unique_tradingsymbol_exchange",
            )
        ]
        managed = True
