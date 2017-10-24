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


class Invitation(models.Model):

    seats = models.IntegerField(default=1)
    email = models.EmailField()
    first_name = models.TextField(max_length=50)
    last_name = models.TextField(max_length=50)
    link_sent = models.BooleanField(blank=True)
    reason = models.TextField()
    event = models.ForeignKey(Event, related_name='invitations')
    products = models.ManyToManyField(Product)

    def is_allowed_to_buy(self, product):
        if len(self.products) == 0:
            return True
        elif self.products.filter(id = product.id).count() > 0:
            return True
        else:
            return False


class Billet(models.Model):

    product = models.ForeignKey(Product, related_name='billets')
    options = models.ManyToManyField(Option, related_name='billets')


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


class Participant(models.Model):

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    billet = models.ForeignKey(Billet, related_name='participants')


class Question(models.Model):

    QUESTIONS_TYPES = (
        (0, _('Champ libre')),
        (1, _('Champ libre (long)')),
        (2, _('Choix multiple')),
        (3, _('Choix multiple et libre')),
        (4, _('Choix')),
        (5, _('Date')),
        (6, _('Date et heure')),
        (7, _('Heure')),
    )

    question = models.CharField(max_length=255)
    help_text = models.TextField()
    question_type = models.IntegerField(verbose_name=_('type de question'))
    required = models.BooleanField(null=True)
    related_prices = models.ManyToManyField(Pricing, related_name='related_questions')


class Response(models.Model):

    question = models.ForeignKey(Question)
    participant = models.ForeignKey(Participant)
    data = models.TextField()


class PaymentMethod(models.Model):
    PROTOCOLS = (
        ("CB", _("payment by Credit Card")),
        ("ESP", _("payment by cash")),
        ("VIR", _("payment by bank transfer"))
    )
    paymentProtocol = models.CharField(max_length=50, choices=PROTOCOLS)
    paymentMin = models.IntegerField(default=-1000000)
    paymentMax = models.IntegerField(default=1000000)

