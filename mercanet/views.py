import hashlib
import json

import datetime
import requests  # bon, urllib est pas content, je change, merci Gab
from django import urls
# Create your views here.
from django.http import HttpResponse, HttpResponseNotFound
from django.http.response import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_exempt

# from mercanet import calculateSeal
from billetterie.settings import BILLEVENT
from mercanet import sealTransaction
from mercanet.models import TransactionMercanet, TransactionRequest, MercanetToken
from mercanet.serializers import TransactionMercanetSerializer

CONFIG = BILLEVENT['MERCANET']


def log(text):
    f = open('mercanet.log', 'a')
    for i in range(len(text)):
        f.write(str(text[i]))
    f.write('\n')
    f.close()


def genId(id):
    return datetime.datetime.now().strftime("%Y%m%d%H") \
           + hashlib.sha1(bytearray(id.encode("UTF-8"))).hexdigest()[:25]


rcList = {
    "00": "Transaction acceptée",
    "02": "Demande d’autorisation par téléphone à la banque à cause d’un dépassement du plafond d’autorisation sur la carte, si vous êtes autorisé à forcer les transactions",
    "03": "Contrat commerçant invalide",
    "05": "Refus 3DSecure",
    "11": "Utilisé dans le cas d'un contrôle différé. Le PAN est en opposition",
    "12": "Transaction invalide, vérifier les paramètres transférés dans la requête",
    "14": "Coordonnées du moyen de paiement invalides (ex: n° de carte ou cryptogramme visuel de la carte) ou vérification AVS échouée",
    "17": "Annulation de l’acheteur",
    "30": "Erreur de format",
    "34": "Suspicion de fraude (seal erroné)",
    "54": "Date de validité du moyen de paiement dépassée",
    "75": "Nombre de tentatives de saisie des coordonnées du moyen de paiement sous Sips Paypage dépassé",
    "90": "Service temporairement indisponible",
    "94": "Transaction dupliquée : le transactionReference de la transaction est déjà utilisé",
    "97": "Délai expiré, transaction refusée",
    "99": "Problème temporaire du serveur de paiement.",
}


class MercanetViewSet:

    @staticmethod
    @csrf_exempt
    def check(request, id):  # va falloir aller chercher dans les DB :(.
        # transactionReference = int(1000 * math.exp(1 + float(id)))
        transactionRequest = TransactionRequest.objects.get(id=id)
        if transactionRequest.status < TransactionRequest.STATUSES['PAYING']:
            return HttpResponseNotFound("NOT DONE YET")
        transactionMercanet = transactionRequest.mercanet
        # utilisation d'un hash pour l'id mercanet
        rc = transactionMercanet.responseCode
        return HttpResponseRedirect(transactionRequest.callback)

    @staticmethod
    def pay(request, id, token):
        transactionRequest = TransactionRequest.objects.get(id=id, token=token)
        amount = transactionRequest.amount

        if transactionRequest.status > TransactionRequest.STATUSES['PAYING']:
            return HttpResponseNotFound("ALREADY DONE")

        # transactionReference = int(1000*math.exp(1+float(id)))
        transactionReference = genId(id)
        mercanetToken = MercanetToken()
        mercanetToken.transactionReference = transactionReference
        mercanetToken.save()  # on enregistre les infos et ça crée un token de transaction pour le serveur

        response = HttpResponse()
        interfaceVersion = CONFIG['INTERFACE_VERSION']
        keyVersion = CONFIG['KEY_VERSION']
        merchantId = CONFIG['MERCHANT_ID']
        normalReturnUrl = request.build_absolute_uri(
            urls.reverse('mercanet-check-payment', args=[transactionRequest.id]))
        urlMercanet = CONFIG['URL']
        automaticResponseUrl = CONFIG['REPONSE_AUTO_URL'] + str(mercanetToken.serverToken)
        donneesPourMercanet = {
            'currencyCode': 978,
            'interfaceVersion': interfaceVersion,
            'keyVersion': keyVersion,
            'merchantId': merchantId,
            'normalReturnUrl': normalReturnUrl,
            'orderChannel': 'INTERNET',
            'amount': amount,
            'transactionReference': transactionReference,
            'automaticResponseUrl': automaticResponseUrl
        }
        seal = sealTransaction.sealFromJson(donneesPourMercanet, CONFIG["SECRET_KEY"], False)
        seal2 = sealTransaction.sealFromList(
            ["978", interfaceVersion, keyVersion, merchantId, normalReturnUrl, "INTERNET", str(amount),
             transactionReference, automaticResponseUrl], CONFIG["SECRET_KEY"])
        donneesPourMercanet['seal'] = seal

        r = requests.post(urlMercanet, json=donneesPourMercanet,
                          verify=False)  # on envoie les données à Mercanet et on enregistre sa réponse
        reponseMercanet = r.json()
        if reponseMercanet["redirectionStatusCode"] == "94":
            return HttpResponse("<h1 style='font-size: 100; color: red'>TRANSACTION DUPLIQUÉE</h1>")
        elif reponseMercanet["redirectionStatusCode"] == "12":
            return HttpResponse("<h1 style='font-size: 100; color: red'>ERREUR SEAL</h1>")
        # reponseMercanet = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8')) #on parse le JSON
        # pas besoin de parser; python-requests le fait tout seul

        redirectionData = reponseMercanet[
            "redirectionData"]  # on extrait les données à insérer dans la page pour le client
        redirectionUrl = reponseMercanet["redirectionUrl"]  # url que le client va appeler
        if (reponseMercanet[
            "redirectionStatusCode"] == "00"):  # si la communication s'est bien passée (et le JSON n'est pas parsé en types)
            context = {
                # charge les données dans la page qu'on renvoie au client, qui le redirigera vers le paiement MercaNET
                "redirectionUrl": redirectionUrl,
                "redirectionData": redirectionData,
                "interfaceVersion": interfaceVersion
            }
            dataToSerialize = {
                "amount": amount,
                "transactionReference": transactionReference,
                "id": id
            }

            # Mise à jour de la request
            transactionRequest.started = True
            transactionRequest.save()

            # dataToSerialize = {}
            # dataToSerialize["amount"]= amount
            # dataToSerialize["transactionReference"]= transactionReference
            # dataToSerialize["id"] = id
            log(["donnés prêtes à être sérializées :transactionReference=", transactionReference, " montant=", amount])

            transaction_data = TransactionMercanetSerializer(data=dataToSerialize, partial=True)
            transaction_data.is_valid()
            for key in transaction_data.errors:
                log([" ser.err>", transaction_data.errors[key]])
            if transaction_data.is_valid():
                transaction = transaction_data.create(transaction_data.validated_data)
                transaction.save()

                transactionRequest.mercanet = transaction
                transactionRequest.save()

                log("transaction saved")
                return TemplateResponse(request, 'mercanet_redirect.html', context)
            else:
                log("serializer invalide")

        else:
            log("erreur de communication avec Mercanet")
            return (response)

    def error(request):
        return HttpResponse("usage : /pay/$id/$token")


@csrf_exempt
def autoMercanet(request,
                 head):  # gère la réponse automatique de MercaNET, seul moyen qu'on ait (dommage) de vérifier un paiement
    fichier = open('req.txt', 'a')
    r = request.POST
    Seal = r.get("Seal")
    log(['seal mercanet : ', Seal])
    log("INCOMING MERCANET REQUEST")
    InterfaceVersion = r.get('InterfaceVersion')
    testSeal = sealTransaction.loneSeal(r.get("Data"), CONFIG["SECRET_KEY"])
    log(['seal recalculé : ', testSeal])
    data = ''.join(r.get("Data")).split(
        '|')  # reconstruit une liste des valeurs, qu'on sépare après pour les mettre dans un JSON
    cles, valeurs = [], []
    json_data = {}
    for i in range(0, len(data)):
        ligne = ''.join(data[i]).split('=')
        cles.append(ligne[0])
        valeurs.append(ligne[1])
        json_data[cles[i]] = valeurs[i]  # on ajoute chaque clé avec sa valeur dans un dictionnaire
    log("json parsé")

    json_final = {  # on génére le JSON que DEVRAIT envoyer MercaNET au lieu de leur format texte de merde
        "InterfaceVersion": InterfaceVersion,
        "Seal": Seal,
        "Data": json_data
    }
    transactionReference = json_data["transactionReference"]
    mercanetToken = MercanetToken.objects.get(transactionReference=transactionReference)
    if mercanetToken.serverToken == head:
        log("Mercanet est correctement authentifié")
    elif MercanetToken.objects.filter(transactionReference=transactionReference)[0] == head or \
            MercanetToken.objects.filter(transactionReference=transactionReference)[1] == head:
        log("entrées dupliquées !")  # ça devrait pas arriver si on repart de 0 sur la BDD Mercanet
    else:
        log("DANGER : MiTM attack ? Mercanet n'a pas répondu à la bonne adresse !!!!")
        exit(1)
    log(head)
    log(mercanetToken.serverToken)
    json_data["responseText"] = rcList[
        json_data['responseCode']]  # on affiche joliment le status (MercaNET) de la commande
    log("status mercanet verbeux rajouté au JSON")
    # json_data.pop("transactionReference")
    # json_data.pop("amount")
    transaction = TransactionMercanet.objects.get(transactionReference=transactionReference)
    log('objet transaction récupéré')
    transaction_data = TransactionMercanetSerializer(transaction, data=json_data, partial=True)
    log(["transaction chargée depuis ID ", transactionReference])

    transaction_data.is_valid()
    for key in transaction_data.errors:
        log([" ser.err>", transaction_data.errors[key]])
    if transaction_data.is_valid():
        log("transaction is valid()")
        transaction_data.update(transaction,
                                transaction_data.validated_data)  # ET PAS UPDATE, si on passe l'objet initial
        transaction.save()
        log("transaction updated")
    else:
        log("erreur lors de la serialisation")

    log(json.dumps(json_final))
    return HttpResponse("merci pour les 0% de commission <3")
