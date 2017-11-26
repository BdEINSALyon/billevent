# librement recopié depuis https://github.com/dentemm/suikerboontje_project/blob/c6cab89daa1129ed87eb84e944f08a0e2a65791d/myapps/sips/gateway.py
# j'en avais marre
from Crypto.Hash import HMAC, SHA256
import hashlib
def sealFromJson(request_dict, cle_secrete):
    concat_string = ''
    for key in sorted(request_dict):
        if key == 'keyVersion':
            continue
        elif key == 'sealAlgorithm':
            continue
        else:
            concat_string += str(request_dict[key])
    message = bytes(concat_string.encode('utf-8'))
    secret = bytes(cle_secrete.encode('utf-8'))
    seal = HMAC.new(key=secret, msg=message, digestmod=SHA256).hexdigest()
    return seal
