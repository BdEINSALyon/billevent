from datetime import datetime

from django.contrib.auth.models import Group
from django.db import models

from django.utils.translation import ugettext_lazy as _


class Organizer(models.Model):
    class Meta:
        verbose_name = _('Organisateur')

    name = models.CharField(max_length=250)
    phone = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=250, blank=True)
    email = models.EmailField()

    def __str__(self):
        return self.name


class Event(models.Model):
    class Meta:
        verbose_name = _('Evènement')

    name = models.CharField(verbose_name=_("Nom de l'évènement"), max_length=255)
    description = models.TextField(verbose_name=_("Description"))
    ticket_background = models.ImageField(verbose_name=_("Fond d'image tickets"), blank=True)
    sales_opening = models.DateTimeField(default=datetime.now, verbose_name=_("Ouverture des ventes"))
    sales_closing = models.DateTimeField(default=datetime.now, verbose_name=_("Clôture des ventes"))
    # Un seats est unique pour un seul participant
    max_seats = models.IntegerField(default=1600, verbose_name=_('Nombre maximal de place'))
    # Utilisé pour des objectifs de statistiques
    seats_goal = models.IntegerField(default=1600, verbose_name=_('Nombre de place visé'))
    logo_url = models.CharField(max_length=2500, verbose_name=_('Url du logo'),
                                default='http://logos.bde-insa-lyon.fr/bal/Logo_bal.png', blank=True,
                                null=True)
    organizer = models.ForeignKey(Organizer, related_name='events', blank=True, null=True)
    # Ouverture des portes
    start_time = models.DateTimeField(verbose_name=_('Début de l\'évènement'), default=datetime.now)
    # Fermeture de l'évènement
    end_time = models.DateTimeField(verbose_name=_('Fin de l\'évènement'), default=datetime.now)
    # Site web de l'évènement
    website = models.CharField(verbose_name=_('Site Web'), max_length=250, blank=True, default="")
    # Nom de la salle
    place = models.CharField(verbose_name=_('Nom du lieu'), max_length=250, blank=True, default="")
    # Adresse de l'évènement
    address = models.CharField(verbose_name=_('Adresse du lieu'), max_length=250, blank=True, default="")

    def __str__(self):
        return self.name

    @property
    def products(self):
        return self.product_set


class Categorie(models.Model):
    name = models.CharField(max_length=50)
    desc = models.CharField(max_length=255, blank=True)
    event = models.ForeignKey(Event,verbose_name=_('Evènements'))

    def __str__(self):
        return self.name


class Pricing(models.Model):
    class Meta:
        verbose_name = _('Tarification')
        abstract = True

    name = models.CharField(max_length=255)
    seats = models.IntegerField(default=1)
    price_ht = models.DecimalField(verbose_name=_('Prix HT'), decimal_places=2, max_digits=11)
    price_ttc = models.DecimalField(verbose_name=_('Prix TTC'), decimal_places=2, max_digits=11)
    rules = models.ManyToManyField("PricingRule", blank=True)
    questions = models.ManyToManyField("Question", blank=True)
    event = models.ForeignKey(Event, verbose_name=_('Evènement'))

    def full_name(self):
        return '{} - {}€'.format(self.name, self.price_ttc)

    @property
    def how_many_left(self) -> int:
        """

        :return: Le nombre de produit restant ou -1 si il en reste une infinité/quantitée indé
        """
        try:
            billets_max = type(self).objects.get(id=self.id).rules.get(type=PricingRule.TYPE_T).value
            nombre_billet = 0
            if self is Product:
                nombre_billet = Billet.objects.filter(product=self.id).count()
            if self is Option:
                nombre_billet = Billet.objects.filter(product=self.id).count()
        except PricingRule.DoesNotExist:
            return -1
        except Billet.DoesNotExist:
            return -1
        else:
            return billets_max-nombre_billet

    def __str__(self):
        return self.name


class Product(Pricing):
    categorie = models.ForeignKey(Categorie, default=1, verbose_name=_('Catégorie'), related_name='products')

    class Meta:
        verbose_name = _('Tarif des produit')

    def __str__(self):
        return self.name+" - "+self.categorie.name


class Option(Pricing):
    class Meta:
        verbose_name = _('Tarif des option')

    products = models.ManyToManyField(Product, related_name='options')


class Invitation(models.Model):
    seats = models.IntegerField(default=1)
    email = models.EmailField()
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    link_sent = models.BooleanField(blank=True)
    reason = models.TextField(blank=True)
    event = models.ForeignKey(Event, related_name='invitations')
    products = models.ManyToManyField(Product, blank=True)

    def is_allowed_to_buy(self, product):
        if len(self.products) == 0:
            return True
        elif self.products.filter(id=product.id).count() > 0:
            return True
        else:
            return False


class Billet(models.Model):
    product = models.ForeignKey(Product, related_name='billets')
    options = models.ManyToManyField(Option, related_name='billets')

    def __str__(self):
        return str("Billet n°" + str(self.id))


class PricingRule(models.Model):
    class Meta:
        verbose_name = _('Règles de poduits (Jauges/Limite')

    TYPE_T = "T"
    TYPE_BYTI = "BYTI"
    TYPE_BYI = "BYI"
    TYPE_VA = "VA"
    RULES = (
        (TYPE_BYI, _("Limit by product by invitation")),
        (TYPE_BYTI, _("Limit by total product by invitation")),
        (TYPE_T, _("Global gap of product")),
        (TYPE_VA, _("Require VA validation (not implemented)"))
    )
    """
        :var type: Le type de règle
        :var description: Sa description
        :var value: ...
    """
    type = models.CharField(max_length=50, choices=RULES)
    description = models.TextField()
    value = models.IntegerField()


    def __str__(self):
        return str(self.type) + " " + str(self.value)


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
    required = models.BooleanField(default=False)


class Response(models.Model):
    question = models.ForeignKey(Question)
    participant = models.ForeignKey(Participant)
    data = models.TextField()


class PaymentMethod(models.Model):
    class Meta:
        verbose_name = _('Moyens de paiement')

    PROTOCOLS = (
        ("CB", _("payment by Credit Card")),
        ("ESP", _("payment by cash")),
        ("VIR", _("payment by bank transfer"))
    )
    paymentProtocol = models.CharField(max_length=50, choices=PROTOCOLS)
    paymentMin = models.IntegerField(default=-1000000)
    paymentMax = models.IntegerField(default=1000000)

    def __str__(self):
        return self.paymentProtocol


class Order(models.Model):
    client = models.ForeignKey(Participant, blank=True, null=True)
    billets = models.ManyToManyField(Billet, blank=True)
    event = models.ForeignKey(Event)


