from django.shortcuts import render
from django.template.response import TemplateResponse
from rest_framework import status
from mercanet import sealTransaction
import os
import json
import urllib.request
import requests #bon, urllib est pas content, je change, merci Gab
# Create your views here.
from time import time
from math import floor
from django.http import HttpResponse
class MercanetViewSet:
    def pay(request, amount):
        réponse = HttpResponse()
        id = int(floor(time()))
        interfaceVersion = os.environ['MERCANET_INTERFACE_VERSION']
        keyVersion = os.environ['MERCANET_KEY_VERSION']
        merchantId = os.environ['MERCANET_MERCHANT_ID']
        normalReturnUrl = os.environ['NORMAL_RETURN_URL']
        urlMercanet = os.environ['MERCANET_URL']
        seal = sealTransaction.sealHash(amount, interfaceVersion, merchantId, normalReturnUrl, id, os.environ['MERCANET_SECRET_KEY'])

        data = {"amount": amount, "currencyCode":978, "interfaceVersion": interfaceVersion,
                "keyVersion" : keyVersion, "merchantId" : merchantId,
                          "normalReturnUrl" : normalReturnUrl, "orderChannel" : "INTERNET",
                "transactionReference" : id, "seal" : seal}
        r = requests.post(urlMercanet, json=data,verify=False)  #on envoie les données à Mercanet et on enregistre sa réponse
        reponseMercanet = r.json()
        réponse.write(reponseMercanet)
        réponse.write('<br><br>')
        réponse.write(seal)

        #reponseMercanet = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8')) #on parse le JSON
        #pas besoin de parser; python-requests le fait tout seul
        try:
            redirectionData = reponseMercanet["redirectionData"]  #on extrait les données à insérer dans la page pour le client
            redirectionUrl = reponseMercanet["redirectionUrl"]      #url que le client va appeler
            if (reponseMercanet["redirectionStatusCode"] == "00"):  # si la communication s'est bien passée
                context = {
                # charge les données dans la page qu'on renvoie au client, qui le redirigera vers le paiement MercaNET
                    "redirectionUrl": redirectionUrl,
                    "redirectionData": redirectionData,
                    "interfaceVersion": interfaceVersion
                }
                return TemplateResponse(request, 'mercanet_redirect.html', context)
            else:
                réponse.write("<br>ha! y'a pas eu assez d'erreurs pour que Django les affiche <3")
            return (réponse)
        except:
            réponse.write("<br><br>JSON type non reçu, Mercanet a dû générer une erreur")


            #reponseAutoFinale = json.loads(rr.read.decode(rr.info().get_param('charset') or 'utf-8'))
    def error(request):
        return HttpResponse("précisez un montant, exprimé en centimes.<br>Ex : 12€35 => /pay/1235")