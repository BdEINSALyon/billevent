# Il est possible qu'il faille intégrer au Seal toutes les données qu'on envoie à MercaNET (dans l'ordre alphabétique des valeurs JSON). Il suffira donc dans ce cas de rajouter les valeurs à la variable DataForSeal
import hmac
import hashlib
def sealHash(montant_a_payer, interface_version, id_boutique, return_url, transaction_id, cle_secrete):
    a = str(montant_a_payer)
    b = str(978) # code ISO4217 désignant les devises en euros €
    d = str(id_boutique)
    e = str(transaction_id)
    cle_encodee = bytearray(cle_secrete.encode("UTF-8"))
    DataForSeal = a + b + interface_version + d + return_url + "INTERNET" + e
    data = bytearray(DataForSeal.encode("UTF-8"))
    seal = hmac.new(cle_encodee, data, hashlib.sha256).hexdigest()
    return seal
def sealFromList(liste, cle_secrete):
    dataForSeal = ""
    for valeur in liste:
        dataForSeal += str(valeur) #rajoute chaque valeur à une string
    data = bytearray(dataForSeal.encode("UTF-8")) #met en forme la grande string
    cle_encodee = bytearray(cle_secrete.encode("UTF-8")) #met en forme la clé secrete

    seal = hmac.new(cle_encodee, data, hashlib.sha256).hexdigest()
    return seal
# cle_secrete : clé identifiant le BdE auprès de Mercanet, à recevoir depuis une variable d'environnement (ne pas stocker sur GitHub !)
#montant_a_payer :  salope, du biff, salope, du biff
#interface_version :  #version du connecteur JSON fait par Mercanet
# id_boutique : identifiant de la boutique mercanet achetée par Torrente
# return_url : URL de retour sur notre site
# transaction_id : ben l'ID de la transaction qu'on fait, que MercaNET utilisera aussi de son côté

