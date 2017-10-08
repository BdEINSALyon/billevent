import hmac
import hashlib
key = "S9i8qClCnb2CZU3y3Vn0toIOgz3z_aBi79akR30vM9o"
#cle_secrete= bytearray(key.encode("utf-8"), "utf-8")  #clé identifiant le BdE auprès de Mercanet, à recevoir depuis une variable d'environnement (ne pas stocker sur GitHub !)
cle_secrete = bytearray("S9i8qClCnb2CZU3y3Vn0toIOgz3z_aBi79akR30vM9o".encode("UTF-8"))
montant_a_payer = 1200 # salope, du biff, salope, du biff
devise_ISO4217 = 978  # code ISO correspondant à une devise en Euros (€)
interface_version = "IR_WS_2.18" #version du connecteur JSON fait par Mercanet
#version_cle = 1 #version de notre clé secrète
id_boutique = 211000021310001 # "Identifiant de la boutique Mercanet" : est-ce lié à notre clé secrète, ou à
return_url = "https://www.marchand.com/normal_return.php"
transaction_id = 123456
def sealHash(montant_a_payer, devise_ISO4217, interface_version, id_boutique, return_url, transaction_id, cle_secrete):
    a = str(montant_a_payer)
    b = str(devise_ISO4217)
    d = str(id_boutique)
    e = str(transaction_id)
    DataForSeal = a + b + interface_version + d + return_url + "INTERNET" + d
    data = bytearray(DataForSeal.encode("UTF-8"))
    seal = hmac.new(cle_secrete, data, hashlib.sha256).hexdigest()
    return seal
seal_de_test = sealHash(montant_a_payer, devise_ISO4217, interface_version, id_boutique, return_url, transaction_id, cle_secrete)
print(seal_de_test)
print("8b3e01a5c2ec76a3954f93bd5ce1ad894a9a8280f68fb9a8b0ffe9523a790e4b")
