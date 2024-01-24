  Le fichier main.py permet de configurer les routeurs du projet GNS3 xxx.

  La configuration se fait à l'aide de telnet : On lit les paramètres de configuration des routeurs dans le json XXX, puis on récupère les commandes à écrire (sans les paramètres) dans le fichier commande.json. On insére dans les commandes pour chaques cas les bons paramètres puis on les écrit sur le routeur via telnet. De plus, après avoir écrit la commmande sur le terminal du routeur, on l'écrit également dans un fichier LastConfig.json. Ce fichier garde seulement en mémoire les suites de commandes apliquées lors de la dernière configuration.
  Si jamais on change les paramètres de configuration des routeurs, on peut les reconfigurer sans les réinitialiser à l'aide des fichier lastConfig. Avant d'entrer une commande dans le terminale on regarde les choses suivantes :
  - Si elle est modifiable : cette information est sous la forme d'un entier dans le fichier commande.json
  - Si elle est différente que la précédente : si c'est le cas et qu'elle est modifiable, on apllique "no" sur la commande précédente avant d'entrer la nouvelle commande et de la garder en mémoire.

  Cela permet de modifier dynamiquement la configuration des routeurs sans les eteindrent : changer rip par ospf, changer d'as, changer de voisin, changer de relation avec le voisin...

  On peut également choisir les routeurs que l'on souhaite configurer ainsi que les élements que l'on souhaite configurer : internalRouting : (rip/ospf), bgp et les interfaces.

  Pour finir, on peut également choisir de supprimer la configuration des protocoles de routage internes, de bgp et des interfaces à l'aide des fonction reset.

  Dernière élements, si on a éteint de le réseau, avant de le rallumer il faut exécuter la fonction clearLastConfig() pour effacer les configurations gardées en mémoires qui ne sont plus sur les routeurs puisque ils ont été éteints.

  

  
