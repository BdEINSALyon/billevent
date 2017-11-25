from django.db import models
import os
import sealTransaction
# Create your models here.

class TransactionMercanet(models.Model):
    class Meta:
        verbose_name = _('Transaction')
        transactionReference =models.IntegerField(verbose_name=_("id de la transaction, le même que MercaNET"))
        amount = models.IntegerField(verbose_name=_("montant payé"))
        maskedPan = models.CharField(verbose_name=_("numéro de CB masqué", max_length=254)
        cardProductName = models.CharField(max_length=100, verbose_name=_("nom de la CB"))
        panExpiryDate = models.IntegerField(max_length=50, verbose_name=_("date d'expiration ?"))
        customerIpAddress = models.IPAddressField(verbose_name=_('On a le droit de le stocker ?'))
        complementaryCode = models.IntegerField(verbose_name=_("C koi ?"))
        panEntryMode = models.CharField(verbose_name=_("mode d'entrée du n° de la CB"))
        captureDay = models.IntegerField()
        responseCode = models.IntegerField(max_length=10, verbose_name=_("utile ?"))
        issuerCountryCode = models.CharField(verbose_name=_("Pays émetteur de la CB"), max_length="5")
        customerMobilePhone = models.CharField(verbose_name=_("numéro de téléphone"), max_length="30")
        paymentMeanBrand = models.CharField(verbose_name=_("organisme de paiement ex: VISA"))
        issuerCode = models.IntegerField(verbose_name=_("C koi ?"))
        transactionDateTime = models.DateTimeCheckMixin(verbose_name=_("Date de la transaction"))
        paymentMeanType = models.CharField(verbose_name=_("type de paiement ex: CB, PayPal..."))
        captureLimitDate = models.IntegerField(verbose_name=_("C koi ? temps pour annuler le paiement ?"))
        cardProductCode = models.CharField(verbose_name=_("important ?"))


