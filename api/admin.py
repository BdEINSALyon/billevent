from django.contrib import admin
from . import models


@admin.register(models.Event,
                models.Organizer,
                models.PricingRule,
                models.Product, models.Option,
                models.Billet,
                models.Invitation,
                models.PaymentMethod,
                models.Question,
                models.Response,
                models.Categorie,
                models.Client,
                models.Participant)
class BasicAdmin(admin.ModelAdmin):
    pass
