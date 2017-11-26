# Il est possible qu'il faille intégrer au Seal toutes les données qu'on envoie à MercaNET (dans l'ordre alphabétique des valeurs JSON). Il suffira donc dans ce cas de rajouter les valeurs à la variable DataForSeal
import hmac
import hashlib
import json
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

def sealVerify(json_data, cle_secrete):
    #json_data = json.load(open('json.txt'))
    Seal = json_data["Seal"]
    Data = json_data["Data"]
    testSeal = sealFromJSON(Data, cle_secrete)
    print(testSeal)
    print(Seal)
    for key in Data:
        print(key)
    if(testSeal == Seal):
        return True
    else:
        return False
#sealVerify("a","S9i8qClCnb2CZU3y3Vn0toIOgz3z_aBi79akR30vM9o")


def sealFromJson(request_dict, cle_secrete, reponse):
    concat_string = ''
    for key in sorted(request_dict):
        if key == 'keyVersion':
            continue
        elif key == 'sealAlgorithm':
            continue
        #elif request_dict[key] == "null":
        #    continue
        else:
            concat_string += str(request_dict[key])
    message = bytearray(concat_string.encode("UTF-8"))
    secret = bytearray(cle_secrete.encode("UTF-8"))
    #seal = HMAC.new(key=secret, msg=message, digestmod=SHA256).hexdigest()
    seal = hmac.new(key=secret, msg=message, digestmod=hashlib.sha256).hexdigest()
    return seal
def loneSeal(data, cle_secrete):
    return hmac.new(key=data.encode('utf-8'), msg=data.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()