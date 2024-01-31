  Le fichier main.py permet de configurer les routeurs du projet GNS3 telnetSetup2.gns3.

  La configuration se fait à l'aide de telnet : On lit les paramètres de configuration des routeurs dans le json DicoRouteur2.json, puis on récupère les commandes à écrire (sans les paramètres) dans le fichier commande.json. On insére dans les commandes pour chaques cas les bons paramètres puis on les écrit sur le routeur via telnet. De plus, après avoir écrit la commmande sur le terminal du routeur, on l'écrit également dans un fichier LastConfig.json. Ce fichier garde en mémoire les suites de commandes apliquées lors des dernières configurations.
  Si jamais on change les paramètres de configuration des routeurs, on peut les reconfigurer sans les réinitialiser à l'aide des fichiers lastConfig.  Pour cela, avant d'écrire une commande avec telnet on regarde les choses suivantes :
  - Si elle est modifiable : cette information est sous la forme d'un entier dans le fichier commande.json
  - Si elle est différente que la précédente : si c'est le cas et qu'elle est modifiable, on applique "no" sur la commande précédente avant d'entrer la nouvelle commande et de la garder en mémoire.
  Cela permet de modifier dynamiquement la configuration des routeurs sans les eteindrent : changer rip par ospf, changer d'as, changer de voisin, changer la relation avec les voisins...

En plus de la configuration dynamique voici les opérations possibles :
  - choix des routeurs que l'on souhaite configurer ainsi que les élements que l'on souhaite configurer : internalRouting : (rip/ospf), bgp et les interfaces (adresses ip et protocole de routage).
  - supression complète de la configuration des protocoles de routage internes, de bgp et des interfaces à l'aide des fonction reset.
  - suppression des configurations gardées en mémoire dans les fichiers LastConfig : Cela est important lorsque les routeurs sont redémarés sans avoir enregistré avec write les configurations précédentes.

Concernant le réseau voici son architecture :
  - 4 AS différentes (111, 222, 333, 444). 
  - Les AS 111,333 et 444 font du rip. L'AS 222 de l'Ospf (avec également les métriques ospf).
  - Les interfaces des routeurs de bordure en OSPF connectées à une autre AS sont en mode passive interface pour que les routeurs de l'as connaissent le next hop en n'évitant de mélanger les deux as.
  - Les interfaces des routeurs de bordure en RIP connectées à une autre AS font du resdistribute connected pour la même raison.
  - Les 4 AS font du bgp.
  - Les AS 111 et 222 sont reliées à une LAN et annoncent en eBGP les réseaux correspondants à leur LAN.
  - Chaques AS tagge les routes recues des AS voisines en fonction de leur relation et leur applique une localPreference correspondante.
  - L'AS 111 applique la politique BGP suivante : Les chemins provenant d'un client ne sont annoncées qu'au peer et au provider, les autres chemins provenant d'un peer ou d'un provider ne sont pas annoncées aux AS voisines.
  

  
