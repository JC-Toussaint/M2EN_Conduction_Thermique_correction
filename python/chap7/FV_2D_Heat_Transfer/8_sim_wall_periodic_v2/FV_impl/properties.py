from FV_lib.struct import Struct

def assign_properties(cfd):
    """
    Assigne les propriétés des matériaux aux régions du maillage CFD
    
    Author: JC Toussaint Grenoble-INP (traduit en Python)
    
    Args:
        cfd: objet Struct contenant les données du maillage
        
    Returns:
        cfd: objet Struct avec les propriétés assignées
    """
                
    # Dictionnaire pour les propriétés : clé = nom de région, valeur = dict des propriétés
    cfd.properties_map = {}
        
    # Définition des propriétés par région    
    cfd.properties_map['isolator']   = Struct(K=2,   Q = lambda x, y: 0)
    cfd.properties_map['metal']      = Struct(K=240, Q = lambda x, y: 0)

    # NE PAS MODIFIER CI-DESSOUS
    # cfd.regionNumber["square"] retourne 17 par exemple
    # cfd.physicalNames[17]["name"] retourne le nom de la région 'square'
    # cfd.properties[17].K permet d'obtenir le coefficient de diffusion 200
    # cfd.properties_map["square"].K retourne 200
    
    # Assigner les propriétés aux régions numérotées
    cfd.properties = {}
    for region_name in cfd.properties_map.keys():
        try:
            # Récupérer le numéro de région
            if region_name in cfd.regionNumber:
                nrg = cfd.regionNumber[region_name]
                cfd.properties[nrg] = cfd.properties_map[region_name]
            else:
                print(f'Attention: Région inconnue "{region_name}" - non trouvée dans regionNumber')
        except Exception as e:
            print(f'Attention: Région inconnue "{region_name}" : {str(e)}')
    
    return cfd