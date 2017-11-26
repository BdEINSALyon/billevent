from datetime import datetime, timedelta

from django.contrib.auth.models import Group, User
from django.db import models
from django.db.models import Sum, Count
from django.db.models.signals import pre_save
from django.dispatch.dispatcher import receiver
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _

TARGETS = (
    ('Order', _('Globalement sur la commande')),
    ('Billet', _('Pour chaque billet')),
    ('Participant', _('Pour chaque participant')),
)


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
    VISIBILITY = (('closed', 'Fermée'), ('hidden', 'Cachée'), ('invite', 'Par invitation'), ('public', 'Public'))

    class Meta:
        verbose_name = _('Evènement')

    name = models.CharField(verbose_name=_("Nom de l'évènement"), max_length=255)
    visibility = models.CharField(max_length=20, choices=VISIBILITY, default='closed', verbose_name=_('Visibilitée'))
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

    @staticmethod
    def for_user(user):
        try:
            client = user.client
            return Event.objects.filter(start_time__gte=timezone.now(), visibility='public') | \
                   Event.objects.filter(invitations__client=client)
        except Client.DoesNotExist:
            return Event.objects.filter(start_time__gte=timezone.now(), visibility='public')


class Categorie(models.Model):
    name = models.CharField(max_length=50)
    desc = models.CharField(max_length=255, blank=True)
    event = models.ForeignKey(Event, verbose_name=_('Evènements'))

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

    def reserved_units(self, billets=None):
        if billets is None:
            billets = Billet.validated()
        if type(self) is Product:
            return billets.filter(product=self).aggregate(total=Count('id'))['total']
        if type(self) is Option:
            return BilletOption.objects.filter(billet__in=billets, option=self) \
                .aggregate(total=Sum('amount'))['total']

    def reserved_seats(self, billets=None):
        return self.reserved_units(billets) * self.seats

    @property
    def how_many_left(self) -> int:
        """

        :return: Le nombre de produit restant ou -1 si il en reste une infinité/quantitée indé
        """
        try:
            billets_max = type(self).objects.get(id=self.id).rules.get(type=PricingRule.TYPE_T).value
            nombre_billet = 0

            if type(self) is Product:
                nombre_billet = Billet.objects.filter(product=self.id).count()
            if type(self) is Option:
                nombre_billet = Billet.objects.filter(options=self.id).count()
        except PricingRule.DoesNotExist:
            return 9999
        except Billet.DoesNotExist:
            return 9999
        else:
            return billets_max - nombre_billet

    def __str__(self):
        return self.name


class Product(Pricing):
    categorie = models.ForeignKey(Categorie, default=1, verbose_name=_('Catégorie'), related_name='products')

    class Meta:
        verbose_name = _('Tarif des produit')

    def __str__(self):
        return self.name + " - " + self.categorie.name


class Option(Pricing):
    class Meta:
        verbose_name = _('Tarif des option')

    products = models.ManyToManyField(Product, related_name='options')
    target = models.CharField(max_length=30, choices=TARGETS, default='Participant')


def generate_token():
    return get_random_string(32)


class Invitation(models.Model):
    seats = models.IntegerField(default=1)
    email = models.EmailField()
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    link_sent = models.BooleanField(blank=True)
    reason = models.TextField(blank=True)
    event = models.ForeignKey(Event, related_name='invitations')
    client = models.ForeignKey('Client', related_name='invitations', null=True, blank=True)
    token = models.CharField(max_length=32, default=generate_token)

    def __str__(self):
        return "Invitation client " + str(self.client)

    @property
    def bought_seats(self):
        billets = Billet.validated().filter(order__client=self.client)
        count = 0
        for pricing in self.event.products.all():
            count += pricing.reserved_seats(billets)
        return count


@receiver(pre_save, sender=Invitation)
def before_save_invitation_map_client(sender, instance, raw, **kwargs):
    if instance.client_id is None:
        instance.client, created = Client.objects.get_or_create(email=instance.email, defaults={
            'first_name': instance.first_name,
            'last_name': instance.last_name
        })


class BilletOption(models.Model):
    """
    Permet de relier une option à un billet
    """

    class Meta:
        verbose_name = _('lien entre une option et un billet')

    billet = models.ForeignKey('Billet', null=True, blank=True, related_name='billet_options')
    option = models.ForeignKey(Option)
    amount = models.IntegerField(default=1)
    participant = models.ForeignKey('Participant', null=True, blank=True, related_name='options_by_billet')


class Billet(models.Model):
    product = models.ForeignKey(Product, null=True, blank=True, related_name='billets')
    options = models.ManyToManyField(Option, through=BilletOption, related_name='billets')
    order = models.ForeignKey('Order', null=True, related_name='billets')

    @staticmethod
    def validated():
        return Billet.objects.filter(
            order__status__lt=Order.STATUS_VALIDATED, order__created_at__gte=timezone.now() - timedelta(minutes=20)
        ) | Billet.objects.filter(order__status=Order.STATUS_VALIDATED)

    def __str__(self):
        return str("Billet n°" + str(self.id))


class PricingRule(models.Model):
    class Meta:
        verbose_name = _('Règles de poduits (Jauges/Limite)')

    TYPE_T = "MaxSeats"
    TYPE_BYTI = "MaxProductByOrder"
    TYPE_BYI = "CheckMaxProductForInvite"
    TYPE_VA = "VA"
    RULES = (
        (TYPE_BYI, _("Vérifie la limite par rapport aux invitations")),
        (TYPE_BYTI, _("Limite le nombre dans une commande")),
        (TYPE_T, _("Limite le nombre de personnes")),
        # (TYPE_VA, _("Require VA validation (not implemented)"))
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

    def validate(self, order):
        """
        Valide l'application de la règle sur une commande
        :type order: Order
        :return:
        """
        if self.type == PricingRule.TYPE_T:
            count = 0
            for pricing in self.pricings:
                count += pricing.reserved_seats()
            return count <= self.value
        elif self.type == PricingRule.TYPE_BYI:
            try:
                invitation = order.client.invitations.get(event=order.event)
                return invitation.seats - invitation.bought_seats >= 0
            except Invitation.DoesNotExist:
                return False
        elif self.type == PricingRule.TYPE_BYTI:
            count = 0
            for pricing in self.pricings:
                count += pricing.reserved_units(order.billets.all())
            return count <= self.value
        elif self.type == PricingRule.TYPE_VA:
            return True
        else:
            return False

    @property
    def pricings(self):
        return list(set(Product.objects.filter(rules=self)).union(set(Option.objects.filter(rules=self))))


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
    target = models.CharField(max_length=30, choices=TARGETS, default='Participant')

    def __str__(self):
        return self.question


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


class Client(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=255, blank=True, null=True)
    user = models.OneToOneField(User, related_name='client', blank=True)

    def __str__(self):
        name = "#" + str(self.id) + " "
        name += self.last_name + " "
        name += self.first_name + " ("
        name += self.email + ")"
        return name


@receiver(pre_save, sender=Client)
def before_save_client_map_user(instance, **kwargs):
    if instance.user_id is None:
        user = None
        try:
            user = User.objects.get(email=instance.email)
        except User.DoesNotExist:
            user = User.objects.create_user(instance.email, instance.email, get_random_string(length=32))
            user.save()
        instance.user = user


class Order(models.Model):

    class Meta:
        verbose_name = _("commande")

    STATUS_NOT_READY = 0
    STATUS_SELECT_PRODUCT = 1
    STATUS_SELECT_OPTIONS = 2
    STATUS_PAYMENT = 3
    STATUS_VALIDATED = 5
    STATUSES = (
        (STATUS_NOT_READY, _('Pas initialisée')),
        (STATUS_SELECT_PRODUCT, _('Sélection des produits')),
        (STATUS_SELECT_OPTIONS, _('Sélection des options')),
        (STATUS_PAYMENT, _('Paiement')),
        (STATUS_VALIDATED, _('Confirmée')),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    client = models.ForeignKey(Client, blank=True, null=True,related_name="orders")
    status = models.IntegerField(verbose_name=_('status'), default=0, choices=STATUSES)
    event = models.ForeignKey(Event)

    def is_valid(self):
        rules = self.sold_products_rules
        for rule in list(rules):
            if not rule.validate(self):
                return False
        return True

    @property
    def amount(self):
        amount = 0
        pricings_sold_into_that_order = self.sold_products
        for pricing in list(pricings_sold_into_that_order):
            amount += pricing.reserved_units(self.billets.all()) * pricing.price_ttc
        return amount

    @property
    def amount_ht(self):
        amount = 0
        pricings_sold_into_that_order = self.sold_products
        for pricing in list(pricings_sold_into_that_order):
            amount += pricing.reserved_units(self.billets.all()) * pricing.price_ht
        return amount

    @property
    def sold_products_rules(self):
        rules = set()
        for products in self.products:
            rules = rules.union(set(products.rules.all()))
        for option in self.options:
            rules = rules.union(set(option.rules.all()))
        return rules

    @property
    def sold_products(self):
        return set(self.products).union(set(self.options))

    @property
    def options(self):
        return Option.objects.filter(billetoption__billet__in=self.billets.all())

    @property
    def products(self):
        return Product.objects.filter(billets__in=self.billets.all())

    def __str__(self):
        return "Commande #" + str(self.event.id) + "-" + str(self.id)

