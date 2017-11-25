from django.shortcuts import render
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes

from mercanet import sealTransaction
import os
import json
import urllib.request
import requests #bon, urllib est pas content, je change, merci Gab
# Create your views here.
from time import time
from math import floor
from django.http import HttpResponse
from rest_framework.response import Response
from django.http import HttpRequest
from rest_framework.parsers import JSONParser
from rest_framework.decorators import parser_classes
class MercanetViewSet:
    def pay(request, amount):
        réponse = HttpResponse()
        id = int(floor(time()))
        interfaceVersion = os.environ['MERCANET_INTERFACE_VERSION']
        keyVersion = os.environ['MERCANET_KEY_VERSION']
        merchantId = os.environ['MERCANET_MERCHANT_ID']
        normalReturnUrl = os.environ['NORMAL_RETURN_URL']
        urlMercanet = os.environ['MERCANET_URL']
        automaticResponseUrl = os.environ['MERCANET_REPONSE_AUTO_URL']
        #seal = sealTransaction.sealHash(amount, interfaceVersion, merchantId, normalReturnUrl, id, os.environ['MERCANET_SECRET_KEY'])
        seal = sealTransaction.sealFromList([amount, automaticResponseUrl, 978, interfaceVersion, merchantId, normalReturnUrl, "INTERNET", id], os.environ["MERCANET_SECRET_KEY"]) #les champs doivent être triés par ordre alphabétique

        data = {"amount": amount, "currencyCode":978, "interfaceVersion": interfaceVersion,
                "keyVersion" : keyVersion, "merchantId" : merchantId,
                          "normalReturnUrl" : normalReturnUrl, "orderChannel" : "INTERNET",
                "transactionReference" : id, "automaticResponseUrl" : automaticResponseUrl,
                "seal" : seal}
        r = requests.post(urlMercanet, json=data,verify=False)  #on envoie les données à Mercanet et on enregistre sa réponse
        reponseMercanet = r.json()
        réponse.write(reponseMercanet)
        réponse.write('<br><br>')
        réponse.write(data)
        réponse.write('<br>')
        réponse.write(seal)

        #reponseMercanet = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8')) #on parse le JSON
        #pas besoin de parser; python-requests le fait tout seul
        try:
            redirectionData = reponseMercanet["redirectionData"]  #on extrait les données à insérer dans la page pour le client
            redirectionUrl = reponseMercanet["redirectionUrl"]      #url que le client va appeler
            if (reponseMercanet["redirectionStatusCode"] == "00"):  # si la communication s'est bien passée (et le JSON n'est pas parsé en types)
                context = {
                # charge les données dans la page qu'on renvoie au client, qui le redirigera vers le paiement MercaNET
                    "redirectionUrl": redirectionUrl,
                    "redirectionData": redirectionData,
                    "interfaceVersion": interfaceVersion
                }
                return TemplateResponse(request, 'mercanet_redirect.html', context)
            else:
                réponse.write("<br>ha! y'a pas eu assez d'erreurs pour que Django les affiche <3")
        except:
            réponse.write("<br><br>JSON type non reçu, Mercanet a dû générer une erreur")
        return (réponse)


            #reponseAutoFinale = json.loads(rr.read.decode(rr.info().get_param('charset') or 'utf-8'))
    def error(request):
        return HttpResponse("précisez un montant, exprimé en centimes.<br>Ex : 12€35 => /pay/1235")
    def check(request, id): #va falloir aller chercher dans les DB :(.
        return HttpResponse(id)
    @csrf_exempt
    def autoMercanet(request, head): #gère la réponse automatique de MercaNET, seul moyen qu'on ait (dommage) de vérifier un paiement
        fichier = open('req.txt', 'a')
        r = request.POST
        Seal = r.get("Seal")
        InterfaceVersion = r.get('InterfaceVersion')
        data = ''.join(r.get("Data")).split('|') #reconstruit une liste des valeurs, qu'on sépare après pour les mettre dans un JSON
        cles, valeurs = [], []
        json_data = {}
        for i in range(0,78):
            ligne = ''.join(data[i]).split('=')
            cles.append(ligne[0])
            valeurs.append(ligne[1])
            json_data[cles[i]] = valeurs[i] # on ajoute chaque clé avec sa valeur dans un dictionnaire
        del json_data["keyVersion"]
        json_data.pop("sealAlgorithm", None)

        json_final = { #on génére le JSON que DEVRAIT envoyer MercaNET au lieu de leur format texte de merde
            "InterfaceVersion" : InterfaceVersion,
            "Seal" : Seal,
            "Data" : json_data
        }
        fichier.write('\n')
        fichier.write(json.dumps(json_final))
        fichier.close()
        fichier = open('req.txt', 'a')
        liste = sorted(json_data)
        testSeal = sealTransaction.sealFromList([valeurs for _,valeurs in sorted(zip(cles,valeurs))], os.environ["MERCANET_SECRET_KEY"])
        if testSeal == Seal:
            fichier.write("\nBRAVO")
        else:
            fichier.write("\nDANGER : SEAL VERIFICATION FAILED\n")
            fichier.write(testSeal)
        fichier.close()




