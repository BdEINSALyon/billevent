from django.db import models
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _


# Create your models here.

def generate_token():
    return get_random_string(127)


class MercanetToken(models.Model):
    class Meta:
        verbose_name_plural = _('identification de Mercanet auprès de billevent')

    serverToken = models.CharField(verbose_name=_('clef d\'identification du serveur Mercanet'), default=generate_token,
                                   max_length=127)
    transactionReference = models.CharField(max_length=35, verbose_name=_(
        'UUID (Référence MercaNET)'))  # oui je sais c'est un duplicata, mais j'en ai besoin avant de créer un objet TransactionMercanet
    mercanet2 = models.OneToOneField('TransactionMercanet', null=True, blank=True)

    def __str__(self):
        return str(self.id) + " - " + self.transactionReference


class TransactionRequest(models.Model):
    class Meta:
        verbose_name = _('Requêtes de paiement')

    STATUSES = {
        'NOT_STARTED': 0,
        'STARTING': 1,
        'PAYING': 2,
        'PAYED': 3,
        'REJECTED': 4
    }
    mercanet = models.OneToOneField('TransactionMercanet', null=True, blank=True, related_name='request')
    amount = models.IntegerField(verbose_name=_('montant en centimes d\'euros'))
    callback = models.CharField(max_length=2000, verbose_name=_('url de retour client'))
    started = models.BooleanField(verbose_name=_('pris en charge par mercanet'), default=False)
    token = models.CharField(verbose_name=_('clef d\'accès'), default=generate_token, max_length=127)

    @property
    def status(self):
        try:
            if self.mercanet is not None:
                if self.mercanet.responseCode == "00":
                    return TransactionRequest.STATUSES['PAYED']
                elif self.mercanet.responseCode is None:
                    return TransactionRequest.STATUSES['PAYING']
                if len(self.mercanet.responseCode) == 2:
                    return TransactionRequest.STATUSES['REJECTED']
                elif self.started:
                    return TransactionRequest.STATUSES['STARTING']
                else:
                    return TransactionRequest.STATUSES['NOT_STARTED']
            return TransactionRequest.STATUSES['NOT_STARTED']
        except TransactionMercanet.DoesNotExist:
            return TransactionRequest.STATUSES['NOT_STARTED']

    def __str__(self):
        return "Request #" + str(self.id) + " - " + str(self.amount / 100) + "€"


class TransactionMercanet(models.Model):
    class Meta:
        verbose_name_plural = _('Transactions avec la BNP')

    id = models.IntegerField(verbose_name=_('id de la commande'), primary_key=True)
    responseText = models.CharField(max_length=256, verbose_name=_('Status de la transaction'), blank=True)
    transactionReference = models.CharField(max_length=35, verbose_name=_('UUID (Référence MercaNET)'))
    amount = models.IntegerField(verbose_name=_("montant payé (centimes)"), primary_key=False, unique=False)
    maskedPan = models.CharField(verbose_name=_("numéro de CB masqué"), max_length=254, blank=True)
    transactionDateTime = models.DateTimeField(verbose_name=_("Date de la transaction"), blank=True, null=True)
    cardProductName = models.CharField(max_length=100, verbose_name=_("nom de la CB"), blank=True)
    panExpiryDate = models.IntegerField(verbose_name=_("date d'expiration ?"), blank=True, null=True)
    customerIpAddress = models.GenericIPAddressField(verbose_name=_('On a le droit de le stocker ?'), blank=True,
                                                     null=True)
    complementaryCode = models.IntegerField(verbose_name=_("C koi ?"), blank=True, null=True)
    panEntryMode = models.CharField(max_length=20, verbose_name=_("mode d'entrée du n° de la CB"), blank=True,
                                    null=True)
    captureDay = models.IntegerField(blank=True, null=True)
    responseCode = models.CharField(max_length=2, verbose_name=_("(responseCode)VERIF PAIEMENT SI=0"), blank=True,
                                    null=True)
    issuerCountryCode = models.CharField(verbose_name=_("Pays émetteur de la CB"), max_length=5, blank=True, null=True)
    customerMobilePhone = models.CharField(verbose_name=_("numéro de téléphone"), max_length=30, blank=True, null=True)
    paymentMeanBrand = models.CharField(max_length=20, verbose_name=_("organisme de paiement ex: VISA"), blank=True,
                                        null=True)
    issuerCode = models.IntegerField(verbose_name=_("C koi ?"), blank=True, null=True)
    paymentMeanType = models.CharField(max_length=20, verbose_name=_("type de paiement ex: CB, PayPal..."), blank=True,
                                       null=True)
    captureLimitDate = models.IntegerField(verbose_name=_("C koi ? temps pour annuler le paiement ?"), blank=True,
                                           null=True)
    cardProductCode = models.CharField(max_length=5, verbose_name=_("important ?"), blank=True, null=True)

    def __str__(self):
        return "Paiement #" + str(self.id) + " - " + str(self.amount / 100) + "€"
