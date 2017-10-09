from datetime import datetime

from django.contrib.auth.models import Group
from django.db import models

from django.utils.translation import ugettext_lazy as _


class Event(models.Model):
    class Meta:
        verbose_name = _('Evènement')

    name = models.CharField(max_length=255)
    description = models.TextField()
    ticket_background = models.ImageField(verbose_name=_("Fond d'image tickets"), blank=True)
    groups = models.ManyToManyField(Group)
    sales_opening = models.DateTimeField(default=datetime.now)
    sales_closing = models.DateTimeField(default=datetime.now)
    # Un seats est unique pour un seul participant
    max_seats = models.IntegerField(default=1600, verbose_name=_('Nombre maximal de place'))
    # Utilisé pour des objectifs de statistiques
    seats_goal = models.IntegerField(default=1600)
    logo_url = models.CharField(max_length=2500, default='http://logos.bde-insa-lyon.fr/bal/Logo_bal.png', blank=True,
                                null=True)


class Pricing(models.Model):
    class Meta:
        verbose_name = _('Tarification')
        abstract = True

    name = models.CharField(max_length=255)
    price_ht = models.DecimalField(verbose_name=_('Prix HT'), decimal_places=2, max_digits=11)
    price_ttc = models.DecimalField(verbose_name=_('Prix TTC'), decimal_places=2, max_digits=11)
    event = models.ForeignKey(Event, verbose_name=_('Evènement'), related_name='entries')
    max_seats = models.IntegerField(default=1600, verbose_name=_('Nombre maximal de place'))

    def full_name(self):
        return '{} - {}€'.format(self.name, self.price_ttc)

    def __str__(self):
        return self.name


class Product(Pricing):
    pass


class Option(Pricing):

    products = models.ManyToManyField(Product, related_name='options')


class PricingRule(models.Model):

    RULES = (
        ("BYI", _("Limit by product by invitation")),
        ("BYTI", _("Limit by total product by invitation")),
        ("T", _("Global gap of product")),
        ("VA", _("Require VA validation (not implemented)"))
    )
    type = models.CharField(max_length=50, choices=RULES)
    description = models.TextField()
    value = models.IntegerField()
    pricings = models.ManyToManyField(Pricing, related_name='rules')


class PaymentMethod(models.Model):
    PROTOCOLS = (
        ("CB", _("payment by Credit Card")),
        ("ESP", _("payment by cash")),
        ("VIR", _("payment by bank transfer"))
    )
    paymentProtocol = models.CharField(max_length=50, choices=PROTOCOLS)
    paymentMin = models.IntegerField(default=-1000000)
    paymentMax = models.IntegerField(default=1000000)
