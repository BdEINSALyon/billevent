# comment qu'ça marche
 * ben le seal il marche pas, MercaNET est méchant
 * et lisez la doc, bonne chance
 
 - l'appli récupère un *token* et un *id*, et regarde dans la base de donnée (mercanetRequest) le montant correspondant.
  - le client suit la procédure de MercaNET
 - il se fait renvoyer (ben oui) sur une page de vérification unique pour lui-même (l'url finit par le *token*)
 - ça vérifie s'il a payé, et met à jour le status pour le rediriger vers une page (genre accueil ou récupération de son billet)

# Faire marcher l'appli de paiement
 Il faut configurer un **proxy POST**, pour recevoir la réponse automatique de MercaNET en local
 (en gros faut écouter le port ``8000`` sur internet) : par exemple, utiliser [Ultrahook](http://www.ultrahook.com/)
 pour tester un paiement, il faut créer une demande de paiement [MercanetRequest](http://localhost:8000/admin/mercanet/transactionrequest/)
 on a de là un *token* et un *id* (indiqué dans la liste, incrémental)
 il faut initier le paiement à l'adresse ``http://localhost:8000/pay/id/token``
 et ensuite c'est bon
