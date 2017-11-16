from django.shortcuts import render
from rest_framework import status
from mercanet import sealTransaction
import os
import json
import urllib.request
# Create your views here.
from math import floor
from math import floor
class MercanetViewSet:
    def pay(amount):
        id = int(floor(time()))
        interfaceVersion = os.environ['MERCANET_INTERFACE_VERSION']
        keyVersion = os.environ['MERCANET_KEY_VERSION']
        merchantId = os.environ['MERCANET_MERCHANT_ID']
        normalReturnUrl = os.environ['NORMAL_RETURN_URL']
        urlMercanet = os.environ['MERCANET_URL']

        sealTransaction.sealHash(amount, interfaceVersion, merchantId, normalReturnUrl, id, os.envion['MERCANET_SECRET_KEY'])

        data = json.dump({"amount": amount, "currencyCode":978, "interfaceVersion": interfaceVersion, "keyVersion":keyVersion, "merchantId": merchantId,
                          "normalReturnUrl" : normalReturnUrl, "orderChannel" : "INTERNET", "transactionReference" : id, "Seal" : sealTransaction})

        r = urllib.request.urlopen(urlMercanet, data=data)  #on envoie les données à Mercanet et on enregistre sa réponse
        reponseMercanet = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8')) #on parse le JSON
        redirectionData = reponseMercanet["redirectionData"]  #on extrait les données à renvoyer à Mercanet
        redirectionUrl = reponseMercanet["redirectionUrl"]
        if(reponseMercanet["redirectionStatusCode"] == 00):   #si la communication s'est bien passée
            finalData = json.dump({"redirectionVersion:" interfaceVersion, "redirectionData": redirectionData})
            rr = urllib.request.urlopen(redirectionUrl, data=finalData)
