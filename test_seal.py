from sealTransaction import sealHash
import sys
cle_secrete = "S9i8qClCnb2CZU3y3Vn0toIOgz3z_aBi79akR30vM9o" #clé identifiant le BdE auprès de Mercanet, à recevoir depuis une variable d'environnement (ne pas stocker sur GitHub !)
montant_a_payer = 1200 # salope, du biff, salope, du biff
devise_ISO4217 = 978  # code ISO correspondant à une devise en Euros (€)
interface_version = "IR_WS_2.18" #version du connecteur JSON fait par Mercanet
#version_cle = 1 #version de notre clé secrète
id_boutique = 211000021310001 # "Identifiant de la boutique Mercanet" : est-ce lié à notre clé secrète, ou à
return_url = "https://www.marchand.com/normal_return.php"
transaction_id = 123456
seal_de_test = sealHash(montant_a_payer, interface_version, id_boutique, return_url, transaction_id, cle_secrete)
seal_exemple = "8b3e01a5c2ec76a3954f93bd5ce1ad894a9a8280f68fb9a8b0ffe9523a790e4b"
print('Seal calculé pour le test :', seal_de_test)
print("Seal qu'on devrait trouver:", seal_exemple)

if(seal_de_test != seal_exemple):
    print("SEALS DO NOT MATCH !!")
    print("TRANSACTIONS WILL FAIL")
    sys.exit(1)
