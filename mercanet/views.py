from django.shortcuts import render
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes

from api.models import Billet
from mercanet import sealTransaction
import os
import json
import urllib.request
import requests #bon, urllib est pas content, je change, merci Gab
# Create your views here.
from time import time
from math import floor
import math
from django.http import HttpResponse
from mercanet.models import TransactionMercanet
from mercanet.serializers import TransactionMercanetSerializer
def log(text):
    f = open('mercanet.log', 'a')
    for i in range(len(text)):
        f.write(str(text[i]))
    f.write('\n')
    f.close()
class MercanetViewSet:
    def check(request, id): #va falloir aller chercher dans les DB :(.
        transactionReference = int(1000 * math.exp(1 + float(id)))
        rc = TransactionMercanet.objects.get(transactionReference=transactionReference).responseCode

    def pay(request, id):
        amount = int(Billet.objects.get(id=id).product.price_ttc * 100)
        transactionReference = int(1000*math.exp(1+float(id)))
        réponse = HttpResponse()
        interfaceVersion = os.environ['MERCANET_INTERFACE_VERSION']
        keyVersion = os.environ['MERCANET_KEY_VERSION']
        merchantId = os.environ['MERCANET_MERCHANT_ID']
        normalReturnUrl = os.environ['NORMAL_RETURN_URL']
        urlMercanet = os.environ['MERCANET_URL']
        automaticResponseUrl = os.environ['MERCANET_REPONSE_AUTO_URL']
        #seal = sealTransaction.sealHash(amount, interfaceVersion, merchantId, normalReturnUrl, transactionReference, os.environ['MERCANET_SECRET_KEY'])
        seal = sealTransaction.sealFromList([amount, automaticResponseUrl, 978, interfaceVersion, merchantId, normalReturnUrl, "INTERNET", transactionReference], os.environ["MERCANET_SECRET_KEY"]) #les champs doivent être triés par ordre alphabétique

        data = {"amount": amount, "currencyCode":978, "interfaceVersion": interfaceVersion,
                "keyVersion" : keyVersion, "merchantId" : merchantId,
                          "normalReturnUrl" : normalReturnUrl, "orderChannel" : "INTERNET",
                "transactionReference" : transactionReference, "automaticResponseUrl" : automaticResponseUrl,
                "seal" : seal}
        r = requests.post(urlMercanet, json=data,verify=False)  #on envoie les données à Mercanet et on enregistre sa réponse
        reponseMercanet = r.json()
        réponse.write(reponseMercanet)
        réponse.write('<br><br>')
        réponse.write(data)
        réponse.write('<br>')
        réponse.write(seal)
        if reponseMercanet["redirectionStatusCode"] == "94":
            return HttpResponse("<h1 style='font-size: 100; color: red'>TRANSACTION   DUPLIQUÉE</h1>")
        #reponseMercanet = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8')) #on parse le JSON
        #pas besoin de parser; python-requests le fait tout seul

        redirectionData = reponseMercanet["redirectionData"]  #on extrait les données à insérer dans la page pour le client
        redirectionUrl = reponseMercanet["redirectionUrl"]      #url que le client va appeler
        if (reponseMercanet["redirectionStatusCode"] == "00"):  # si la communication s'est bien passée (et le JSON n'est pas parsé en types)
            context = {
            # charge les données dans la page qu'on renvoie au client, qui le redirigera vers le paiement MercaNET
                "redirectionUrl": redirectionUrl,
                "redirectionData": redirectionData,
                "interfaceVersion": interfaceVersion
            }
            dataToSerialize = {}
            dataToSerialize["amount"]= amount
            dataToSerialize["transactionReference"]= transactionReference
            log(["donnés prêtes à être sérializées :transactionReference=", transactionReference, " montant=", amount])

            transaction_data = TransactionMercanetSerializer(data=dataToSerialize, partial=True)
            if transaction_data.is_valid():
                transaction = transaction_data.create(transaction_data.validated_data)
                transaction.save()
                log("transaction saved")
                return TemplateResponse(request, 'mercanet_redirect.html', context)
            else: log("serializer invalide")
        #   transaction_data = TransactionMercanetSerializer(data=dataToSerialize)
        #   log(["utilisateur va envoyé au paiement transactionReference= ",data["transactionReference", "amount= ", amount]])
        #   if transaction_data.is_valid():
        #       log("transaction is valid()")
        #       transaction = transaction_data.create(transaction_data.validated_data)
        #       transaction.save()
        #       log("transaction saved")
        #       return TemplateResponse(request, 'mercanet_redirect.html', context)
        #   else:
        #       log("transaction invalide (partie BDD)")
        #       return HttpResponse("erreur interne BDD")
        else:
            réponse.write("<br>ha! y'a pas eu assez d'erreurs pour que Django les affiche <3")
            log("erreur de communication avec Mercanet")
            return (réponse)


            #reponseAutoFinale = json.loads(rr.read.decode(rr.info().get_param('charset') or 'utf-8'))
    def error(request):
        return HttpResponse("précisez un montant, exprimé en centimes.<br>Ex : 12€35 => /pay/1235")

    @csrf_exempt
    def autoMercanet(request, head): #gère la réponse automatique de MercaNET, seul moyen qu'on ait (dommage) de vérifier un paiement
        fichier = open('req.txt', 'a')
        r = request.POST
        Seal = r.get("Seal")
        log("INCOMING MERCANET REQUEST")
        InterfaceVersion = r.get('InterfaceVersion')
        data = ''.join(r.get("Data")).split('|') #reconstruit une liste des valeurs, qu'on sépare après pour les mettre dans un JSON
        cles, valeurs = [], []
        json_data = {}
        for i in range(0,78):
            ligne = ''.join(data[i]).split('=')
            cles.append(ligne[0])
            valeurs.append(ligne[1])
            json_data[cles[i]] = valeurs[i] # on ajoute chaque clé avec sa valeur dans un dictionnair
        del json_data["keyVersion"] # il ne faut pas les intégrer dans le calcul du Seal
        json_data.pop("sealAlgorithm", None)   # autre méthode, on l'enlève

        json_final = { #on génére le JSON que DEVRAIT envoyer MercaNET au lieu de leur format texte de merde
            "InterfaceVersion" : InterfaceVersion,
            "Seal" : Seal,
            "Data" : json_data
        }
        transactionReference = json_data["transactionReference"]
        #json_data.pop("transactionReference")
        #json_data.pop("amount")
        transaction = TransactionMercanet.objects.get(transactionReference=transactionReference)
        transaction_data = TransactionMercanetSerializer(transaction, data=json_data, partial=True)
        log(["transaction chargée depuis ID ", transactionReference])

        transaction_data.is_valid()
        for key in transaction_data.errors:
            log([" ser.err>",transaction_data.errors[key]])
        if transaction_data.is_valid():
            log("transaction is valid()")
            transaction_data.update(transaction, transaction_data.validated_data) # ET PAS UPDATE, si on passe l'objet initial
            transaction.save()
            log("transaction updated")
        else: log("erreur lors de la serialisation")
   #    transaction_data = TransactionMercanetFinalSerializer(data=json_data)
   #    log("transaction OK")
   #    if transaction_data.is_valid():
   #        log("transaction is valid()")
   #        transaction = transaction_data.create(transaction, transaction_data.validated_data)
   #        transaction.update()
   #        log("transaction saved")

        fichier.write('\n')
        fichier.write(json.dumps(json_final))
        fichier.close()
        fichier = open('req.txt', 'a')
        testSeal = sealTransaction.sealFromList([valeurs for _,valeurs in sorted(zip(cles,valeurs))], os.environ["MERCANET_SECRET_KEY"])
        if testSeal == Seal:
            fichier.write("\nBRAVO")
        else:
            fichier.write("\nDANGER : SEAL VERIFICATION FAILED\n")
            fichier.write(testSeal)
        fichier.close()
        return HttpResponse("merci pour les 0% de commission <3")