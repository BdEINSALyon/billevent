from django.contrib import admin
from . import models


@admin.register(models.Event,
                models.Organizer,
                models.Membership,
                models.PricingRule,
                models.Product, models.Option,
                models.Coupon,
                models.Billet,
                models.BilletOption,
                models.Invitation,
                models.PaymentMethod,
                models.Question,
                models.Response,
                models.Categorie,
                models.Client,
                models.Participant)
class BasicAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'event', 'client', 'status', 'mercanet', 'created_at', 'amount']
    search_fields = ['client__first_name', 'client__last_name', 'client__email', 'transaction__mercanet__transactionReference']
    list_display_links = ['id']
    list_filter = ['event', 'status']
    list_per_page = 20

    def mercanet(self, order):
        if order.transaction:
            return order.transaction.mercanet.transactionReference
        else:
            return ''

    def amount(self, o):
        return "{}€".format(o.amount)
