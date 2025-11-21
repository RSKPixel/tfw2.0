from django.db import models


# Create your models here.
class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    zerodha_user_id = models.CharField(
        max_length=100, unique=True, null=True, blank=True
    )
    zerodha_api_key = models.CharField(max_length=100, null=True, blank=True)
    zerodha_api_secret = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = "tfw_users"
        managed = True
