from django.db import models
from django.utils.translation import ugettext_lazy as _
# Create your models here.

class TransactionMercanet(models.Model):
    class Meta:
        verbose_name = _('Transaction avec la BNP')
        verbose_name_plural = _('Transaction avec la BNP')
    id = models.IntegerField(verbose_name=_('id de la commande'), primary_key=True)
    responseText = models.CharField(max_length=256, verbose_name=_('Status de la transaction'), blank=True)
    transactionReference = models.CharField(max_length=35 ,verbose_name=_('UUID (Référence MercaNET)'))
    amount = models.IntegerField(verbose_name=_("montant payé (centimes)"), primary_key=False, unique=False)
    maskedPan = models.CharField(verbose_name=_("numéro de CB masqué"), max_length=254, blank=True)
    transactionDateTime = models.DateTimeField(verbose_name=_("Date de la transaction"), blank=True, null=True)
    cardProductName = models.CharField(max_length=100, verbose_name=_("nom de la CB"), blank=True)
    panExpiryDate = models.IntegerField(verbose_name=_("date d'expiration ?"), blank=True, null=True)
    customerIpAddress = models.GenericIPAddressField(verbose_name=_('On a le droit de le stocker ?'), blank=True, null=True)
    complementaryCode = models.IntegerField(verbose_name=_("C koi ?"), blank=True, null=True)
    panEntryMode = models.CharField(max_length=20,verbose_name=_("mode d'entrée du n° de la CB"), blank=True, null=True)
    captureDay = models.IntegerField(blank=True, null=True)
    responseCode = models.CharField(max_length=2, verbose_name=_("(responseCode)VERIF PAIEMENT SI=0"), blank=True, null=True)
    issuerCountryCode = models.CharField(verbose_name=_("Pays émetteur de la CB"), max_length=5, blank=True, null=True)
    customerMobilePhone = models.CharField(verbose_name=_("numéro de téléphone"), max_length=30, blank=True, null=True)
    paymentMeanBrand = models.CharField(max_length=20,verbose_name=_("organisme de paiement ex: VISA"), blank=True, null=True)
    issuerCode = models.IntegerField(verbose_name=_("C koi ?"), blank=True, null=True)
    paymentMeanType = models.CharField(max_length=20,verbose_name=_("type de paiement ex: CB, PayPal..."), blank=True, null=True)
    captureLimitDate = models.IntegerField(verbose_name=_("C koi ? temps pour annuler le paiement ?"), blank=True, null=True)
    cardProductCode = models.CharField(max_length=5,verbose_name=_("important ?"), blank=True, null=True)
    def __str__(self):
        return str(self.id)