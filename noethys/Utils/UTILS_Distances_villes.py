#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


def GetDistances(origine="", destinations=[], moyen="voiture") :
    """ R�cup�re sur Googlemaps les distances entre les villes """
    dictResultats = {}

    # Recherche le moyen de locomotion
    if moyen == "velo" :
        mode = "bicycling"
    elif moyen == "marche" :
        mode = "walking"
    else:
        mode = "driving"

    try :

        # Cr�ation de la requete URL

        # Formatage du texte d'origine
        if isinstance(origine, tuple) :
            texteOrigine = "%20".join(origine)
        else :
            texteOrigine = origine
        texteOrigine = texteOrigine.replace(" ", "%20")

        # Formatage du texte des destinations
        if not isinstance(destinations, list) :
            destinations = [destinations,]

        liste_destinations = []
        for destination in destinations :
            if isinstance(destination, tuple):
                texteDestinations = "%20".join(destination)
            else:
                texteDestinations = destination
            texteDestinations = texteDestinations.replace(" ", "%20")
            liste_destinations.append(texteDestinations)
        texteDestinations = "|".join(liste_destinations)
        url = """http://maps.googleapis.com/maps/api/distancematrix/json?origins=%s&destinations=%s&sensor=false&mode=%s&language=fr-FR&userip=192.168.1.1""" % (texteOrigine, texteDestinations, mode)

        # R�cup�re les distances sur Google maps
        import urllib2
        # Conversion des accents
        url = urllib2.quote(url.encode('utf8'), ":/?=.-%&,")

        # Ouverture de l'url
        f = urllib2.urlopen(url, timeout=10)
        texteReponse = f.read()
        
        # Transforme le r�sultat en dictionnaire Python
        import json
        dictReponse = json.loads(texteReponse)
        
        index = 0
        for destination in destinations :
            donnees = dictReponse["rows"][0]["elements"][index]
            if donnees["status"] == "OK" :
                temps_texte = donnees["duration"]["text"]
                temps_secondes = donnees["duration"]["value"]
                distance_metres = donnees["distance"]["value"]
                distance_texte = donnees["distance"]["text"]

                dictResultats[destination] = {
                    "temps_texte" : temps_texte,
                    "temps_secondes" : temps_secondes,
                    "distance_metres" : distance_metres,
                    "distance_texte" : distance_texte,
                    }
                    
            index += 1
    
    except :
        dictResultats = {}
        
    return dictResultats


if __name__ == '__main__':


    # Test avec coordonn�es GPS
    dictResultats = GetDistances(origine="46.539464, 6.646241", destinations="46.538994, 6.651082", moyen="marche")

    # Test avec plusieurs villes de destination
    #dictResultats = GetDistances(origine=("29870", "LANNILIS"), destinations=[("29200", "BREST"), ("29000", "QUIMPER")], moyen="voiture")

    # Affichage des r�sultats
    for key, resultat in dictResultats.iteritems() :
        print key, " ->", resultat
