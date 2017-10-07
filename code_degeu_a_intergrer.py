<?php
  $SecretKey = "S9i8qClCnb2CZU3y3Vn0toIOgz3z_aBi79akR30vM9o";
  $PaymentRequest = '{"amount" : "1200","currencyCode" : "978","interfaceVersion" : "IR_WS_2.18","keyVersion" : "1","merchantId" : "211000021310001","normalReturnUrl" : "https://www.marchand.com/normal_return.php","orderChannel" : "INTERNET,"transactionReference" : "123456","seal" : "fac5bc8e5396d77a8b31a2a79a38750feea71b22106a2cec88efa3641a947345"}';
  $DataForSeal = "1200978IR_WS_2.18211000021310001https://www.marchand.com/normal_return.phpINTERNET123456";   // Valeur des champs triés sur le nom des champs
  $DataToSend = utf8_encode($DataForSeal);                   // conversion du champ DataForSeal en UTF8
  $Seal=hash_hmac('sha256', $DataToSend, $SecretKey);        // hmac avec un hash du champ DatatToSend crypté par la clé secrète 
  
  echo "Seal = ".$Seal;
?>
cle_secrete = ''  #clé identifiant le BdE auprès de Mercanet, à recevoir depuis une variable d'environnement (ne pas stocker sur GitHub !)
montant_a_payer = 1200 # salope, du biff, salope, du biff
devise_ISO4217 = 978  # code ISO correspondant à une devise en Euros (€)
interface_version = "IR_WS_2.18" #version du connecteur JSON fait par Mercanet
version_cle = 1 #version de notre clé secrète
id_billevent = 211000021310001 # "Identifiant de la boutique Mercanet" : est-ce lié à notre clé secrète, ou à 

def sealHash(cle_secrete):

