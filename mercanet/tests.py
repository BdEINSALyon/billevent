from django.test import TestCase
from mercanet import sealTransaction
#Pour les tests, il faut penser à ajouter aux options de lancement des test unitaires la variable d'environnement DJANGO_SETTINGS_MODULE à la valeur billetterie.settings
#
# Create your tests here.
class MercanetTests(TestCase):
    def test_Hash(self):
        #On teste si l'exemple donné par la BNP marche
        self.assertEquals("8b3e01a5c2ec76a3954f93bd5ce1ad894a9a8280f68fb9a8b0ffe9523a790e4b",sealTransaction.sealHash(1200,"IR_WS_2.18",211000021310001,"https://www.marchand.com/normal_return.php",123456,"S9i8qClCnb2CZU3y3Vn0toIOgz3z_aBi79akR30vM9o"))
        #On teste que si l'on modifie l'exemple de la BNP ça ne marche pas
        self.assertNotEquals("8b3e01a5c2ec76a3954f93bd5ce1ad894a9a8280f68fb9a8b0ffe9523a790e4b",
                          sealTransaction.sealHash(1200, "AH!IR_WS_2.18", 211000021310001,
                                                   "https://www.marchand.com/normal_return.php", 123456,
                                                   "S9i8qClCnb2CZU3y3Vn0toIOgz3z_aBi79akR30vM9o"))
        #On teste que si l'on appelle la fonction avec les mêmes paramètres elle renvoie bien le même Hash (Inutile ?)
        self.assertEquals(sealTransaction.sealHash(1,"hg",5,"fgh.php",522,"AH!"),sealTransaction.sealHash(1,"hg",5,"fgh.php",522,"AH!"))