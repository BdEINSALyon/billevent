from django.contrib import admin
from . import models


@admin.register(models.Event,
                models.PricingRule,
                models.Product, models.Option,
                models.Billet,
                models.Invitation,
                models.PaymentMethod,
                models.Question, models.Response)
class BasicAdmin(admin.ModelAdmin):
    pass
