import time
import json

def ip_address(name,neighbor):
    """
    Parameters
    ----------
    name : Int : numéro de routeur
    neighbor : Int : numéro du routeur voisin
    Returns
    -------
    res : int :valeur correspondant au sous-réseau entre les deux routeurs
    Cette valeur est utilisée pur configurer leurs adresses ip.
    """
    if neighbor == "EXIT" :
        res = 1
    elif name < neighbor :
        res = name*10 + neighbor
    else :
        res = neighbor*10 + name
    return res 

def setNeighborVal(neighborType) :
    """
    Parameters
    ----------
    neighborType : Chaine de caractère (peer, provider ou customer)
    Returns
    -------
    res : Entier
        Retourne un entier en fonction du type de relation avec l'AS voisine.
        Cette entier est utilisé pour attribuer la localPref ainsi que les numéros
        de communauté.
    """
    if  neighborType == "customer" :
         res = 500
    elif  neighborType == "peer":
         res = 300
    elif  neighborType == "provider":
         res = 100
    else :
         res = 0
    return res

def write(lastConfig, key, com, lvl, indice, tn) :
    """
    Parameters
    ----------
    lastConfig : Dictionnaire contenant la dernière configuration du routeur
    key : Clef du dictionnaire lastConfig.
    com : String : Commande que l'on veut rentrer.
    lvl : Si lvl == 0, la commande est modifiable, si non, on ne peut pas la
        modifier (ex: configure terminal)
    indice : Int : Correspond à l'indice de la liste contenant la suite des
        anciennes commandes.
    tn : telnet
    -------
    Fonction vérifiant si la nouvelle commande est différente de la précédente.
    Si la commande est différente : on applique "no" devant l'ancienne et on 
    l'écrit sur le routeur pour la supprimer.
    Après avoir écrit la nouvelle commande sur le routeur, on la garde en mémoire
    dans le dictionnaire de LastConfig.
    """
    if lvl == 0 : #si la commande est changeable
        if key in lastConfig.keys() :
            if indice <= len(lastConfig[key])-1: #important pour la premiere config
                lastCom = lastConfig[key][indice]
                if com != lastCom: #Si la commande est différente de la précédente
                    if lastCom[0] == "n" and lastCom[1] == "o":
                        noCom = lastCom[2:]
                    else :
                        noCom = "no " + lastCom
                    #print(noCom)

                    tn.write(noCom.encode('utf-8')) #On enleve la commande précédente
                    tn.read_until(b"#")  
    #print(com)
    tn.write(com.encode('utf-8')) #On écrit la nouvelle commande 
    tn.read_until(b"#")
    
    #On ajoute la nouvelle commande dans le fichier qui garde en mémoire les commandes entrées 
    if key not in lastConfig.keys() :
        lastConfig[key] = [com] 
    elif len(lastConfig[key]) -1 < indice : #important si l'indice dépasse la taille de la liste
        lastConfig[key].append(com) 
    else :
        lastConfig[key][indice] = com 

def internalRoutingProtocol(routeur, conf, commande,tn):
    """
    Parameters
    ----------
    name : Chaine de caractère : nom du routeur 
    conf : Dictionnaire contenant la configuration de chaques routeur du réseau.
    commande : Dictionnaire contenant les commandes de configuration d'un routeur cisco.
    tn : telnetlib.Telnet
    Returns
    -------
    None. Ecrit sur le teminal du routeur les commandes pour configurer le protocol de routage interne.

    """
    with open(f"lastConfig/lastConfig{routeur}.json","r") as f:
        lastConfig = json.load(f)
    
    routing_protocol = conf['routing_protocol'] #Récupération du protocol de routage intra-domaine
    border = conf['border'] #Récupération du booléen indiquant si le routeur est un routeur de bordure
    
    ### Configuration du protocol de routage interne ###
    if border == 'True'  and routing_protocol == 'ospf':
        for i in range(len(commande['internalRouting']['ospfbordure'])) :
            comDico = commande['internalRouting']['ospfbordure'][i]
            for com, lvl in comDico.items():
                com= com.format(name=routeur)
                write(lastConfig, 'internalRouting',com, lvl, i, tn)
                    
    elif border == 'True' and routing_protocol == 'rip' :
        for i in range(len(commande['internalRouting']['ripbordure'])) :
            comDico = commande['internalRouting']['ripbordure'][i]
            for com, lvl in comDico.items() :
                com= com.format(name=routeur)
                write(lastConfig, 'internalRouting',com, lvl, i, tn)
                    
    else :
        for i in range(len(commande['internalRouting'][routing_protocol])):
            comDico = commande['internalRouting'][routing_protocol][i]
            for com, lvl in comDico.items() :
                com= com.format(name=routeur)
                write(lastConfig, 'internalRouting', com, lvl, i, tn)
            
                

    #Si la nouvelle suite de commande est plus petite que la précédente
    if i < len(lastConfig['internalRouting'])  :
        for j in range(i+1, len(lastConfig['internalRouting'])):
            del lastConfig['internalRouting'][i+1]
            
    
    with open(f"lastConfig/lastConfig{routeur}.json","w") as f:
        json.dump(lastConfig, f)
    tn.write(b"end\r") 
    tn.read_until(b"#")

def noInternalRoutingProtocol(routeur,conf, commande,tn):
    """
    Parameters
    ----------
    name : Chaine de caractère : nom du routeur 
    conf : Dictionnaire contenant la configuration de chaques routeur du réseau.
    commande : Dictionnaire contenant les commandes de configuration d'un routeur cisco.
    tn : telnetlib.Telnet
    Returns
    -------
    Supprimer les commandes pour configurer le protocol de routage interne.

    """
   
    with open(f"lastConfig/lastConfig{routeur}.json","r") as f:
         lastConfig = json.load(f)
     
    routing_protocol = conf['routing_protocol']
    if routing_protocol == 'ospf':
         for i in range(len(commande['internalRouting']['resetOspf'])) :
             comDico = commande['internalRouting']['resetOspf'][i]
             for com, lvl in comDico.items():
                 write(lastConfig, 'internalRouting',com, lvl, i, tn)
    else :
        for i in range(len(commande['internalRouting']['resetRip'])) :
            comDico = commande['internalRouting']['resetRip'][i]
            for com, lvl in comDico.items():
                write(lastConfig, 'internalRouting',com, lvl, i, tn)
            
     
    tn.write(b"end\r")  
    tn.read_until(b"#")
     
    if i < len(lastConfig['internalRouting'])  :
         for j in range(i+1, len(lastConfig['internalRouting'])):
             del lastConfig['internalRouting'][i+1] 
             
    with open(f"lastConfig/lastConfig{routeur}.json","w") as f:
         json.dump(lastConfig, f)


def interfaceConfig(name, conf, commande,tn):
    """
    Parameters
    ----------
    name: Chaine de caractère : nom du routeur 
    conf : Dictionnaire contenant la configuration de chaques routeur du réseau.
    commande : Dictionnaire contenant les commandes de configuration d'un routeur cisco.
    tn : telnetlib.Telnet
    Returns
    -------
    Configure chaques interface du routeur.
    """
    with open(f"lastConfig/lastConfig{name}.json","r") as f:
        lastConfig = json.load(f)
        
    routing_protocol = conf['routing_protocol']
    AS = conf['as']
    neighbors = conf['neighbors']
    for interface, neighbor in neighbors.items() :

        if neighbor[0] != "NULL" :
            ip_val = ip_address(name, neighbor[0])
            
            ## Ecriture de commande obligatoire pour accéder aux interfaces
            for i in range(len(commande['interface'][interface])):
                comDico = commande['interface'][interface][i]
                for com, _ in comDico.items():
                    tn.write(com.encode('utf-8'))
                    tn.read_until(b"#")
                
            ## Pour les interfaces de bordure et le protocol rip
            if interface == "0" and routing_protocol == "rip" :
                for i in range(len(commande['interface']['no'])) :
                    comDico = commande['interface']['no'][i]
                    for com, lvl in comDico.items():
                        com= com.format(name=name, ip_val = ip_val, AS = 3)
                        if 'interface' not in lastConfig.keys():
                            lastConfig['interface'] = {}
                        write(lastConfig['interface'], interface ,com, lvl, i, tn)
                    
            else :
                for i in range(len(commande['interface'][routing_protocol])):
                    comDico = commande['interface'][routing_protocol][i]
                    for com, lvl in comDico.items():
                        if routing_protocol == "rip" :
                            valcost = 0
                        else :
                            valcost = neighbor[1]
            
                        if interface == "0" :
                            com= com.format(name=name, ip_val = ip_val, AS = 3, cost = valcost)
                        else :
                            com= com.format(name=name, ip_val = ip_val, AS = AS, cost = valcost)
                            
                        if 'interface' not in lastConfig.keys():
                            lastConfig['interface'] = {}
                        write(lastConfig['interface'], interface ,com, lvl, i, tn)
                        
            tn.write(b"end\r") 
            tn.read_until(b"#")
            #Si la nouvelle suite de commande est plus petite que la précédente
            if i < len(lastConfig['interface'][interface])  :
                for j in range(i+1, len(lastConfig['interface'][interface])):
                    del lastConfig['interface'][interface][i+1]   
             
    with open(f"lastConfig/lastConfig{name}.json","w") as f:
        json.dump(lastConfig, f)
   

def noInterfaceConfig(name, conf, commande,tn):
    """
    Parameters
    ----------
    name : Chaine de caractère : nom du routeur 
    conf : Dictionnaire contenant la configuration de chaques routeur du réseau.
    commande : Dictionnaire contenant les commandes de configuration d'un routeur cisco.
    tn : telnetlib.Telnet
    Returns
    -------
    Réinitialise chaques interface du routeur.
    """
    with open(f"lastConfig/lastConfig{name}.json","r") as f:
         lastConfig = json.load(f)
     
    routing_protocol = conf['routing_protocol']
    AS = conf['as']
    neighbors = conf['neighbors']
  
    for interface, neighbor in neighbors.items() : # pour tous les voisins sur chaques interfaces 
        if neighbor[0] != "NULL" :
            ip_val = ip_address(name, neighbor[0])
            for i in range(len(commande['interface'][interface])) :
                comDico = commande['interface'][interface][i]
                for com, _ in comDico.items():  
                    tn.write(com.encode('utf-8'))
                    tn.read_until(b"#")
                    
            if interface == "0" and routing_protocol == "rip" :
                for i in range(len(commande['interface']['resetno'])) :
                    comDico = commande['interface']['resetno'][i]
                    for com, lvl in comDico.items():
                        com = com.format(name=name, ip_val = ip_val, AS = 3)
                        write(lastConfig['interface'], interface,com, lvl, i, tn)
                
            else :
                if routing_protocol == "rip" :
                    valcost = 0
                else :
                    valcost = neighbor[1]
                    
                for i in range(len(commande['interface']['reset'+routing_protocol])) :
                     comDico = commande['interface']['reset'+routing_protocol][i]
                     for com, lvl in comDico.items():
                         if interface == "0" :
                             com= com.format(name=name, ip_val = ip_val, AS = 3, cost = valcost)
                         else :
                             com= com.format(name=name, ip_val = ip_val, AS = AS, cost = valcost )
                         write(lastConfig['interface'], interface,com, lvl, i, tn)
                
                         
              
            tn.write(b"end\r") 
            tn.read_until(b"#")
            
            if i < len(lastConfig['interface'][interface])  :
                   for j in range(i+1, len(lastConfig['internalRouting'])):
                       del lastConfig['internalRouting'][i+1] 
                       
    with open(f"lastConfig/lastConfig{name}.json","w") as f:
           json.dump(lastConfig, f)
                    
    
def bgpConfig (name, conf, commande,tn) :
    """
    Parameters
    ----------
    name : Chaine de caractère : nom du routeur 
    conf : Dictionnaire contenant la configuration de chaques routeur du réseau.
    commande : Dictionnaire contenant les commandes de configuration d'un routeur cisco.
    tn : telnetlib.Telnet
    Returns
    -------
    Configure bgp sur le routeur.
    """
    with open(f"lastConfig/lastConfig{name}.json","r") as f:
        lastConfig = json.load(f)
        
    AS = conf['as']
    border = conf['border']
    neighbors = conf['neighbors']
    ASrouter = conf['ASrouter']
    AS_neighbor = conf['ASneighbor']
    
    indice = 0
    
    for i in range(len(commande['bgp']['config'])):
        comDico = commande['bgp']['config'][i]
        for com, lvl in comDico.items():
            com = com.format(name=name, AS = AS)
            write(lastConfig, 'bgp',com, lvl, indice, tn)
        indice +=1
      
        
    for router in ASrouter :
        ip_val = ip_address(router, router)
        if border == "True" :
            session = "internalSessionBorder"
        else :
            session = "internalSession"
        for i in range(len(commande['bgp'][session])) :
            comDico = commande['bgp'][session][i]
            for com, lvl in comDico.items():
                com= com.format(name=router, ip_val = ip_val, AS = AS)
                write(lastConfig, 'bgp',com, lvl, indice, tn)
            indice +=1
        time.sleep(1)
         


    if border == "True" :
        #time.sleep(1)
        if conf["filter"] == "False" :
            session = "externalSession"
        else :
            neighborType = conf["neighborRelationship"]
            if neighborType == "provider" or neighborType == "peer" :
                session = "externalSessionPP"
            else :
                session = "externalSessionC"
                
        for i in range(len(commande['bgp'][session])) :
            ip_val = ip_address(name,neighbors["0"][0])
            comDico = commande['bgp'][session][i]
            for com, lvl in comDico.items():
                com = com.format(name=neighbors['0'][0], ip_val = ip_val, AS_neighbor = AS_neighbor)
                write(lastConfig, 'bgp',com, lvl, indice, tn)
            indice +=1
            
 
        advertise = conf['advertise']
        for network_number in advertise :
            comDico = commande['bgp']['advertise']
            for com, lvl in comDico.items():
                com = com.format(ip_val = network_number, AS = AS)
                write(lastConfig, 'bgp',com, lvl, indice, tn)
            indice +=1
                
    tn.write(b"end\r") 
    tn.read_until(b"#")
    #Si la nouvelle suite de commande est plus petite que la précédente
    
    if indice < len(lastConfig['bgp'])  :
        for j in range(indice+1, len(lastConfig['bgp'])):
            del lastConfig['bgp'][indice+1]   
        

    with open(f"lastConfig/lastConfig{name}.json","w") as f:
        json.dump(lastConfig, f)
    
def noBgpConfig(name,conf, commande, tn):
    """
    Parameters
    ----------
    name : Chaine de caractère : nom du routeur 
    conf : Dictionnaire contenant la configuration de chaques routeur du réseau.
    commande : Dictionnaire contenant les commandes de configuration d'un routeur cisco.
    tn : telnetlib.Telnet
    Returns
    -------
    Réinitalise la configuration bgp sur le routeur.
    """
    with open(f"lastConfig/lastConfig{name}.json","r") as f:
        lastConfig = json.load(f)
    
    AS = conf['as']
    for i in range(len(commande['bgp']['reset'])) :
        comDico = commande['bgp']['reset'][i]
        for com, lvl in comDico.items():
            com = com.format(AS = AS)
            write(lastConfig, 'bgp',com, lvl, i, tn)
    
    tn.write(b"end\r")  
    tn.read_until(b"#")
    
    if i < len(lastConfig['bgp'])  :
        for j in range(i+1, len(lastConfig['bgp'])):
            del lastConfig['bgp'][i+1]
            
    #lastConfig['bgp'] = {}
    with open(f"lastConfig/lastConfig{name}.json","w") as f:
        json.dump(lastConfig, f)
        

def setCommunity(name, conf, commande, tn):
    """
    Parameters
    ----------
    name : Chaine de caractère : nom du routeur 
    conf : Dictionnaire contenant la configuration de chaques routeur du réseau.
    commande : Dictionnaire contenant les commandes de configuration d'un routeur cisco.
    tn : telnetlib.Telnet
    Returns
    -------
    Configure les communautés sur un routeur de bordure.
    """
    with open(f"lastConfig/lastConfig{name}.json","r") as f:
        lastConfig = json.load(f)
        
    AS = conf['as']
    neighborType = conf["neighborRelationship"]
    neighborVal = setNeighborVal(neighborType)
    for i in range(len(commande['setCommunity']) ):
        comDico = commande['setCommunity'][i]
        for com, lvl in comDico.items():
            com = com.format(neighborType = neighborVal , AS = AS)
            write(lastConfig, 'setCommunity',com, lvl, i, tn)
            
    if i < len(lastConfig['setCommunity'])  :
         for j in range(i+1, len(lastConfig['setCommunity'])):
             del lastConfig['setCommunity'][i+1]
            
    with open(f"lastConfig/lastConfig{name}.json","w") as f:
         json.dump(lastConfig, f)
                
    tn.write(b"end\r")  
    tn.read_until(b"#")
    

def filterCommunity(name, conf, commande, tn) :
    """
    Parameters
    ----------
    name : Chaine de caractère : nom du routeur 
    conf : Dictionnaire contenant la configuration de chaques routeur du réseau.
    commande : Dictionnaire contenant les commandes de configuration d'un routeur cisco.
    tn : telnetlib.Telnet
    Returns
    -------
    Fonction créant les route-map pour filtrer les communautées.
    """
    with open(f"lastConfig/lastConfig{name}.json","r") as f:
        lastConfig = json.load(f)
    neighborType = conf["neighborRelationship"]
    
    # Si le voisin est un provider ou un peer, on lui donne que les chemins des clients
    # On permit que la communauté des clients 
    if neighborType == "provider" or neighborType == "peer" :
        AS = conf['as']
        for i in range(len(commande['filterCommunityPeerProvider']) ):
            comDico = commande['filterCommunityPeerProvider'][i]
            for com, lvl in comDico.items():
                com = com.format(AS= AS)
                write(lastConfig, 'filterCommunityPeerProvider',com, lvl, i, tn)
        
        if i < len(lastConfig['filterCommunityPeerProvider'])  :
             for j in range(i+1, len(lastConfig['filterCommunityPeerProvider'])):
                 del lastConfig['filterCommunityPeerProvider'][i+1]
                    
        tn.write(b"end\r")  
        tn.read_until(b"#")
        
    # Si le voisin est un client, on ne lui donne pas de chemins
    # On deny tout
    else :
        for i in range(len(commande["filterCommunityCustomer"]) ):
            comDico = commande["filterCommunityCustomer"][i]
            for com, lvl in comDico.items():
                write(lastConfig, "filterCommunityCustomer",com, lvl, i, tn)
                
       
        if i < len(lastConfig['filterCommunityCustomer'])  :
             for j in range(i+1, len(lastConfig['filterCommunityCustomer'])):
                 del lastConfig['filterCommunityCustomer"'][i+1]
                    
                    
        tn.write(b"end\r")  
        tn.read_until(b"#")
        
    
    with open(f"lastConfig/lastConfig{name}.json","w") as f:
         json.dump(lastConfig, f)
    
def resetFilterCommunity(name, conf, commande, tn) :
    """
    Parameters
    ----------
    name : Chaine de caractère : nom du routeur 
    conf : Dictionnaire contenant la configuration de chaques routeur du réseau.
    commande : Dictionnaire contenant les commandes de configuration d'un routeur cisco.
    tn : telnetlib.Telnet
    Returns
    -------
    Fonction supprimant les route-map pour filtrer les communautées.
    """
    with open(f"lastConfig/lastConfig{name}.json","r") as f:
        lastConfig = json.load(f)
    neighborType = conf["neighborRelationship"]
    
   
    if neighborType == "provider" or neighborType == "peer" :
        AS = conf['as']
        for i in range(len(commande['nofilterCommunityPeerProvider']) ):
            comDico = commande['nofilterCommunityPeerProvider'][i]
            for com, lvl in comDico.items():
                com = com.format(AS= AS)
                write(lastConfig, 'filterCommunityPeerProvider',com, lvl, i, tn)
                
        if i < len(lastConfig['filterCommunityPeerProvider'])  :
             for j in range(i+1, len(lastConfig['filterCommunityPeerProvider'])):
                 del lastConfig['filterCommunityPeerProvider'][i+1]
                    
        tn.write(b"end\r")  
        tn.read_until(b"#")
        
    
    else :
        for i in range(len(commande["nofilterCommunityCustomer"]) ):
            comDico = commande["nofilterCommunityCustomer"][i]
            for com, lvl in comDico.items():
                write(lastConfig, "filterCommunityCustomer",com, lvl, i, tn)
                
        if i < len(lastConfig['filterCommunityCustomer'])  :
             for j in range(i+1, len(lastConfig['filterCommunityCustomer'])):
                 del lastConfig['filterCommunityCustomer'][i+1]
                    
        tn.write(b"end\r")  
        tn.read_until(b"#")
        
    
    with open(f"lastConfig/lastConfig{name}.json","w") as f:
         json.dump(lastConfig, f)
    

def resetCommunity(name,conf,commande,tn) :
    """
    Parameters
    ----------
    name : Chaine de caractère : nom du routeur 
    conf : Dictionnaire contenant la configuration de chaques routeur du réseau.
    commande : Dictionnaire contenant les commandes de configuration d'un routeur cisco.
    tn : telnetlib.Telnet
    Returns
    -------
    Efface la configuration des communautés sur un routeur de bordure.
    """
    with open(f"lastConfig/lastConfig{name}.json","r") as f:
        lastConfig = json.load(f)
        
    for i in range(len(commande['resetCommunity'])):
        comDico = commande["resetCommunity"][i]
        for com, lvl in comDico.items():
            write(lastConfig, "setCommunity",com, lvl, i, tn)
            
        
    tn.write(b"end\r")  
    tn.read_until(b"#")
    
    if i < len(lastConfig['setCommunity'])  :
        for j in range(i+1, len(lastConfig['setCommunity'])):
            del lastConfig['setCommunity'][i+1]
            
    with open(f"lastConfig/lastConfig{name}.json","w") as f:
          json.dump(lastConfig, f)
