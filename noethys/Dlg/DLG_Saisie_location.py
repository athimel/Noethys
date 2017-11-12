#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import Chemins
from Utils.UTILS_Traduction import _
import wx
import datetime
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Questionnaire
from Ctrl import CTRL_Logo
from Ctrl import CTRL_Saisie_date
from Ctrl import CTRL_Saisie_heure
from Utils import UTILS_Titulaires
from Utils import UTILS_Dates
from Utils import UTILS_Customize
from Utils import UTILS_Locations
from Dlg import DLG_Messagebox
import GestionDB
from Ol import OL_Locations_prestations



class CTRL_Loueur(wx.TextCtrl):
    def __init__(self, parent):
        wx.TextCtrl.__init__(self, parent, -1, style=wx.TE_READONLY)
        self.parent = parent
        self.IDfamille = None
        self.IDcompte_payeur = None

    def SetIDfamille(self, IDfamille=None):
        self.IDfamille = IDfamille

        # Recherche du nom des titulaires
        dictNomsTitulaires = UTILS_Titulaires.GetTitulaires([self.IDfamille, ])
        nomsTitulaires = dictNomsTitulaires[self.IDfamille]["titulairesSansCivilite"]
        self.IDcompte_payeur = dictNomsTitulaires[self.IDfamille]["IDcompte_payeur"]
        self.SetValue(nomsTitulaires)

    def GetIDfamille(self):
        return self.IDfamille

    def GetIDcomptePayeur(self):
        return self.IDcompte_payeur




class CTRL_Produit(wx.TextCtrl):
    def __init__(self, parent):
        wx.TextCtrl.__init__(self, parent, -1, style=wx.TE_READONLY)
        self.parent = parent
        self.IDproduit = None
        self.IDcategorie = None

    def SetIDproduit(self, IDproduit=None):
        self.IDproduit = IDproduit

        # Recherche des caract�ristiques du produit
        db = GestionDB.DB()
        req = """SELECT produits.nom, produits.IDcategorie, produits.observations, produits.image, produits_categories.nom
        FROM produits 
        LEFT JOIN produits_categories ON produits_categories.IDcategorie = produits.IDcategorie
        WHERE IDproduit=%d;""" % self.IDproduit
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        if len(listeDonnees) > 0 :
            nomProduit, IDcategorie, observations, image, nomCategorie = listeDonnees[0]
            label = u"%s (%s)" % (nomProduit, nomCategorie)
        else :
            IDcategorie = None
            label = ""
            observations = ""
            image = None

        # Nom
        self.SetValue(label)

        # M�morise IDcategorie (sert pour mesure de la distance)
        self.IDcategorie = IDcategorie

        # Logo
        self.parent.ctrl_logo.ChargeFromBuffer(image)


    def GetIDproduit(self):
        return self.IDproduit

    def GetIDcategorie(self):
        return self.IDcategorie



# -----------------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Parametres(wx.Notebook):
    def __init__(self, parent, IDlocation=None):
        wx.Notebook.__init__(self, parent, id=-1, style=wx.BK_DEFAULT | wx.NB_MULTILINE)
        self.dictPages = {}
        self.IDlocation = IDlocation

        self.listePages = [
            {"code": "questionnaire", "ctrl": Page_Questionnaire(self, self.IDlocation), "label": _(u"Questionnaire"), "image": "Questionnaire.png"},
            {"code": "facturation", "ctrl": Page_Facturation(self, self.IDlocation), "label": _(u"Prestations"), "image": "Euro.png"},
        ]

        # ImageList pour le NoteBook
        il = wx.ImageList(16, 16)
        self.dictImages = {}
        for dictPage in self.listePages:
            self.dictImages[dictPage["code"]] = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/%s" % dictPage["image"]), wx.BITMAP_TYPE_PNG))
        self.AssignImageList(il)

        # Cr�ation des pages
        self.dictPages = {}
        index = 0
        for dictPage in self.listePages:
            self.AddPage(dictPage["ctrl"], dictPage["label"])
            self.SetPageImage(index, self.dictImages[dictPage["code"]])
            self.dictPages[dictPage["code"]] = dictPage["ctrl"]
            index += 1

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)

    def GetPageAvecCode(self, codePage=""):
        return self.dictPages[codePage]

    def AffichePage(self, codePage=""):
        index = 0
        for dictPage in self.listePages:
            if dictPage["code"] == codePage:
                self.SetSelection(index)
            index += 1

    def OnPageChanged(self, event):
        """ Quand une page du notebook est s�lectionn�e """
        if event.GetOldSelection() == -1: return
        indexPage = event.GetSelection()
        page = self.GetPage(indexPage)
        self.Freeze()
        wx.CallLater(1, page.Refresh)
        self.Thaw()
        event.Skip()

    def Validation(self):
        for dictPage in self.listePages :
            if dictPage["ctrl"].Validation() == False :
                return False
        return True

    def GetDonnees(self):
        dictDonnees = {}
        for dictPage in self.listePages :
            for key, valeur in dictPage["ctrl"].GetDonnees().iteritems() :
                dictDonnees[key] = valeur
        return dictDonnees

    def SetDonnees(self, dictDonnees={}):
        for dictPage in self.listePages :
            dictPage["ctrl"].SetDonnees(dictDonnees)

    def SetTexteOnglet(self, code, texte=""):
        index = 0
        for dictPage in self.listePages :
            if dictPage["code"] == code :
                self.SetPageText(index, texte)
            index += 1



# -----------------------------------------------------------------------------------------------------------------------------------------------------------


class Page_Questionnaire(wx.Panel):
    def __init__(self, parent, IDlocation=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDlocation = IDlocation
        self.ctrl_questionnaire = CTRL_Questionnaire.CTRL(self, type="location", IDdonnee=self.IDlocation)

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_base.Add(self.ctrl_questionnaire, 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(sizer_base)
        self.Layout()

    def Validation(self):
        return True

    def GetDonnees(self):
        return {}

    def SetDonnees(self, dictDonnees={}):
        pass



class Page_Facturation(wx.Panel):
    def __init__(self, parent, IDlocation=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDlocation = IDlocation

        self.listviewAvecFooter = OL_Locations_prestations.ListviewAvecFooter(self, kwargs={"dlg_saisie_location" : self.GetGrandParent()})
        self.ctrl_prestations = self.listviewAvecFooter.GetListview()
        self.ctrl_prestations.SetMinSize((50, 50))

        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))

        # Properties
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter une prestation")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier la prestation s�lectionn�e dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer la prestation s�lectionn�e dans la liste")))

        # Bind
        self.Bind(wx.EVT_BUTTON, self.ctrl_prestations.Ajouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_prestations.Modifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.ctrl_prestations.Supprimer, self.bouton_supprimer)

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)

        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_base.Add(self.listviewAvecFooter, 0, wx.EXPAND, 0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=4, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_boutons, 0, 0, 0)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(0)

        sizer_base.Add(grid_sizer_base, 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(sizer_base)
        self.Layout()

    def MAJ(self):
        self.ctrl_prestations.MAJ()

    def Validation(self):
        return True

    def GetDonnees(self):
        dictDonnees = {"prestations": self.ctrl_prestations.GetTracks()}
        return dictDonnees

    def SetDonnees(self, dictDonnees={}):
        if dictDonnees.has_key("prestations") and len(dictDonnees["prestations"]) > 0:
            self.ctrl_prestations.SetPrestations(dictDonnees["prestations"])



# -----------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, IDlocation=None, IDfamille=None, IDproduit=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDlocation = IDlocation
        self.liste_initiale_IDprestation = []

        if self.IDlocation == None :
            self.SetTitle(_(u"Saisie d'une location"))
        else :
            self.SetTitle(_(u"Modification d'une location"))

        # G�n�ralit�s
        self.staticbox_generalites_staticbox = wx.StaticBox(self, -1, _(u"G�n�ralit�s"))
        self.label_loueur = wx.StaticText(self, -1, _(u"Loueur :"))
        self.ctrl_loueur = CTRL_Loueur(self)
        self.ctrl_loueur.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, 'Arial'))
        self.bouton_loueur = wx.Button(self, -1, _(u"S�lectionner"))

        self.label_produit = wx.StaticText(self, -1, _(u"Produit :"))
        self.ctrl_produit = CTRL_Produit(self)
        self.ctrl_produit.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, 'Arial'))
        self.bouton_produit = wx.Button(self, -1, _(u"S�lectionner"))

        self.label_observations = wx.StaticText(self, -1, _(u"Notes :"))
        self.ctrl_observations = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE)

        # Logo
        self.staticbox_logo_staticbox = wx.StaticBox(self, -1, _(u"Image du produit"))
        self.ctrl_logo = CTRL_Logo.CTRL(self, qualite=100, couleurFond=wx.Colour(255, 255, 255), size=(110, 110), mode="lecture")
        self.bouton_visualiser = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Loupe.png"), wx.BITMAP_TYPE_ANY))

        # P�riode
        self.staticbox_periode_staticbox = wx.StaticBox(self, -1, _(u"P�riode de location"))
        self.label_date_debut = wx.StaticText(self, -1, _(u"D�but :"))
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.ctrl_heure_debut = CTRL_Saisie_heure.Heure(self)
        self.check_date_fin = wx.CheckBox(self, -1, _(u"Fin :"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        self.ctrl_heure_fin = CTRL_Saisie_heure.Heure(self)

        # Quantit�
        self.staticbox_quantite_staticbox = wx.StaticBox(self, -1, _(u"Quantit�"))
        self.ctrl_quantite = wx.SpinCtrl(self, -1, min=1)
        self.ctrl_quantite.SetMinSize((80, -1))
        self.ctrl_quantite.SetValue(1)

        # Param�tres
        self.ctrl_parametres = CTRL_Parametres(self, self.IDlocation)
        self.ctrl_parametres.SetMinSize((650, 270))

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_outils = CTRL_Bouton_image.CTRL(self, texte=_(u"Outils"), cheminImage="Images/32x32/Configuration.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHECKBOX, self.OnCheckDateFin, self.check_date_fin)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOutils, self.bouton_outils)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.ctrl_logo.Visualiser, self.bouton_visualiser)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonLoueur, self.bouton_loueur)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonProduit, self.bouton_produit)

        # Init contr�les
        maintenant = datetime.datetime.now()
        self.ctrl_date_debut.SetDate(datetime.datetime.strftime(maintenant, "%Y-%m-%d"))
        self.ctrl_heure_debut.SetHeure(datetime.datetime.strftime(maintenant, "%H:%M"))

        if self.IDlocation != None :
            self.Importation()

        if IDfamille != None :
            self.ctrl_loueur.SetIDfamille(IDfamille)
            self.bouton_loueur.Show(False)

        if IDproduit != None :
            self.ctrl_produit.SetIDproduit(IDproduit)

        self.ctrl_parametres.GetPageAvecCode("questionnaire").ctrl_questionnaire.MAJ()
        self.OnCheckDateFin()

    def __set_properties(self):
        self.ctrl_loueur.SetToolTip(wx.ToolTip(_(u"Nom du loueur")))
        self.ctrl_produit.SetToolTip(wx.ToolTip(_(u"Nom du produit")))
        self.bouton_loueur.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour s�lectionner un loueur")))
        self.bouton_produit.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour s�lectionner un produit")))
        self.ctrl_observations.SetToolTip(wx.ToolTip(_(u"Saisissez ici des observations �ventuelles")))
        self.ctrl_logo.SetToolTip(wx.ToolTip(_(u"Image du produit")))
        self.bouton_visualiser.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour visualiser l'image actuelle en taille r�elle")))

        self.ctrl_date_debut.SetToolTip(wx.ToolTip(_(u"Saisissez la date de d�but de location")))
        self.ctrl_heure_debut.SetToolTip(wx.ToolTip(_(u"Saisissez l'heure de d�but de location")))
        self.check_date_fin.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour d�finir la date de fin de location")))
        self.ctrl_date_fin.SetToolTip(wx.ToolTip(_(u"Saisissez la date de fin de location")))
        self.ctrl_heure_fin.SetToolTip(wx.ToolTip(_(u"Saisissez l'heure de fin de location")))
        self.ctrl_quantite.SetToolTip(wx.ToolTip(_(u"Saisissez une quantit�")))

        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_outils.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour acc�der aux outils")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider la saisie")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler et fermer")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)

        grid_sizer_haut = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)

        # G�n�ralit�s
        staticbox_generalites = wx.StaticBoxSizer(self.staticbox_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)

        grid_sizer_generalites.Add(self.label_loueur, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_loueur = wx.FlexGridSizer(1, 2, 5, 5)
        grid_sizer_loueur.Add(self.ctrl_loueur, 0, wx.EXPAND, 0)
        grid_sizer_loueur.Add(self.bouton_loueur, 0, 0, 0)
        grid_sizer_loueur.AddGrowableCol(0)
        grid_sizer_generalites.Add(grid_sizer_loueur, 1, wx.EXPAND, 0)

        grid_sizer_generalites.Add(self.label_produit, 0, wx.ALIGN_RIGHT| wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_produit = wx.FlexGridSizer(1, 2, 5, 5)
        grid_sizer_produit.Add(self.ctrl_produit, 0, wx.EXPAND, 0)
        grid_sizer_produit.Add(self.bouton_produit, 0, 0, 0)
        grid_sizer_produit.AddGrowableCol(0)
        grid_sizer_generalites.Add(grid_sizer_produit, 1, wx.EXPAND, 0)

        grid_sizer_generalites.Add(self.label_observations, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_generalites.Add(self.ctrl_observations, 0, wx.EXPAND, 0)
        grid_sizer_generalites.AddGrowableCol(1)
        grid_sizer_generalites.AddGrowableRow(2)
        staticbox_generalites.Add(grid_sizer_generalites, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_haut.Add(staticbox_generalites, 1, wx.EXPAND, 10)

        # Logo
        staticbox_logo = wx.StaticBoxSizer(self.staticbox_logo_staticbox, wx.VERTICAL)
        grid_sizer_logo = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_logo_boutons = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_logo.Add(self.ctrl_logo, 0, wx.EXPAND, 0)
        grid_sizer_logo_boutons.Add(self.bouton_visualiser, 0, 0, 0)
        grid_sizer_logo.Add(grid_sizer_logo_boutons, 1, wx.EXPAND, 0)
        grid_sizer_logo.AddGrowableRow(0)
        grid_sizer_logo.AddGrowableCol(0)
        staticbox_logo.Add(grid_sizer_logo, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_haut.Add(staticbox_logo, 1, wx.EXPAND, 0)

        grid_sizer_haut.AddGrowableCol(0)
        grid_sizer_haut.AddGrowableRow(0)
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.TOP|wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        grid_sizer_milieu = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)

        # P�riode
        staticbox_periode = wx.StaticBoxSizer(self.staticbox_periode_staticbox, wx.VERTICAL)
        grid_sizer_periode = wx.FlexGridSizer(rows=1, cols=8, vgap=5, hgap=5)
        grid_sizer_periode.Add(self.label_date_debut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_periode.Add(self.ctrl_heure_debut, 0, 0, 0)
        grid_sizer_periode.Add( (10, 5), 0, 0, 0)
        grid_sizer_periode.Add(self.check_date_fin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 0, 0, 0)
        grid_sizer_periode.Add(self.ctrl_heure_fin, 0, 0, 0)
        staticbox_periode.Add(grid_sizer_periode, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_milieu.Add(staticbox_periode, 1, wx.EXPAND, 0)

        # Quantit�
        staticbox_quantite = wx.StaticBoxSizer(self.staticbox_quantite_staticbox, wx.VERTICAL)
        staticbox_quantite.Add(self.ctrl_quantite, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_milieu.Add(staticbox_quantite, 1, wx.EXPAND, 0)

        grid_sizer_milieu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_milieu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Questionnaire
        grid_sizer_base.Add(self.ctrl_parametres, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_outils, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(2)
        self.Layout()
        self.SetMinSize(self.GetSize())
        self.CenterOnScreen()

    def OnBoutonLoueur(self, event):
        from Dlg import DLG_Selection_famille
        dlg = DLG_Selection_famille.Dialog(self, IDfamille=self.ctrl_loueur.GetIDfamille())
        if dlg.ShowModal() == wx.ID_OK:
            IDfamille = dlg.GetIDfamille()
            self.ctrl_loueur.SetIDfamille(IDfamille)
        dlg.Destroy()

    def OnBoutonProduit(self, event):
        from Dlg import DLG_Selection_produit
        dlg = DLG_Selection_produit.Dialog(self, IDproduit=self.ctrl_produit.GetIDproduit())
        if dlg.ShowModal() == wx.ID_OK:
            IDproduit = dlg.GetIDproduit()
            self.ctrl_produit.SetIDproduit(IDproduit)
        dlg.Destroy()

    def OnCheckDateFin(self, event=None):
        self.ctrl_date_fin.Enable(self.check_date_fin.GetValue())
        self.ctrl_heure_fin.Enable(self.check_date_fin.GetValue())
        self.ctrl_date_fin.SetFocus()

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonOutils(self, event):
        # Cr�ation du menu contextuel
        menuPop = wx.Menu()

        # Item Mesurer
        item = wx.MenuItem(menuPop, 10, _(u"Mesurer une distance"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Transport.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Mesurer_distance, id=10)

        # Contr�le
        if UTILS_Customize.GetValeur("referentiel", "url", None, ajouter_si_manquant=False) != None:
            item = wx.MenuItem(menuPop, 20, _(u"Contr�le r�f�rentiel"))
            item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Personnes.png"), wx.BITMAP_TYPE_PNG))
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Controle_referentiel, id=20)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Mesurer_distance(self, event):
        from Dlg import DLG_Mesure_distance
        dictParametres = {
            "IDfamille" : self.ctrl_loueur.GetIDfamille(),
            "IDproduit" : self.ctrl_produit.GetIDproduit(),
            "IDcategorie" : self.ctrl_produit.GetIDcategorie(),
        }
        dlg = DLG_Mesure_distance.Dialog(self, dictParametres=dictParametres)
        dlg.ShowModal()
        dlg.Destroy()

    def Controle_referentiel(self, event):
        from Dlg import DLG_Controle_referentiel
        dictParametres = {
            "IDfamille" : self.ctrl_loueur.GetIDfamille(),
        }
        dlg = DLG_Controle_referentiel.Dialog(self, dictParametres=dictParametres)
        dlg.ShowModal()
        dlg.Destroy()

    def GetDictInfosLocation(self):
        dictInfos = {
            "IDproduit" : self.ctrl_produit.GetIDproduit(),
            "quantite" : int(self.ctrl_quantite.GetValue()),
        }
        return dictInfos

    def OnBoutonOk(self, event):
        # Loueur
        IDfamille = self.ctrl_loueur.GetIDfamille()
        if IDfamille == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement s�lectionner un loueur pour ce produit !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Produit
        IDproduit = self.ctrl_produit.GetIDproduit()
        if IDproduit == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement s�lectionner un produit !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Observations
        observations = self.ctrl_observations.GetValue()

        # Date de d�but
        date_debut = self.ctrl_date_debut.GetDate()
        if date_debut == None:
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de d�but de location !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return

        heure_debut = self.ctrl_heure_debut.GetHeure()
        if heure_debut == None or self.ctrl_heure_debut.Validation() == False:
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une heure de d�but valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_heure_debut.SetFocus()
            return

        date_debut = datetime.datetime(year=date_debut.year, month=date_debut.month, day=date_debut.day, hour=int(heure_debut[:2]), minute=int(heure_debut[3:]))

        # Date de fin
        if self.check_date_fin.GetValue() == True :

            date_fin = self.ctrl_date_fin.GetDate()
            if date_fin == None:
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de fin de location !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_date_fin.SetFocus()
                return

            heure_fin = self.ctrl_heure_fin.GetHeure()
            if heure_fin == None or self.ctrl_heure_fin.Validation() == False:
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une heure de fin valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_heure_fin.SetFocus()
                return

            date_fin = datetime.datetime(year=date_fin.year, month=date_fin.month, day=date_fin.day, hour=int(heure_fin[:2]), minute=int(heure_fin[3:]))

        else :
            date_fin = None

        if date_fin != None and date_debut > date_fin:
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de fin sup�rieure � la date de d�but !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus()
            return

        # Quantit�
        quantite = int(self.ctrl_quantite.GetValue())

        # V�rifie que la quantit� demand�e est disponible
        dictPeriodes = UTILS_Locations.GetStockDisponible(IDproduit=IDproduit, date_debut=date_debut, date_fin=date_fin, IDlocation_exception=self.IDlocation)
        liste_periode_non_dispo = []
        for periode, valeurs in dictPeriodes.iteritems() :
            if valeurs["disponible"] < quantite :
                debut = datetime.datetime.strftime(periode[0], "%d/%m/%Y-%Hh%M")
                if periode[1].year == 2999 :
                    fin = _(u"Illimit�")
                else :
                    fin = datetime.datetime.strftime(periode[1], "%d/%m/%Y-%Hh%M")
                liste_periode_non_dispo.append(_(u"Stock disponible du %s au %s : %d produits") % (debut, fin, valeurs["disponible"]))
        if len(liste_periode_non_dispo) > 0 :
            introduction = _(u"La quantit� souhait�e n'est pas disponible sur les p�riodes suivantes :")
            conclusion = _(u"Vous ne pouvez pas valider la location.")
            dlg = DLG_Messagebox.Dialog(None, titre=_(u"Information"), introduction=introduction, detail=u"\n".join(liste_periode_non_dispo), conclusion=conclusion, icone=wx.ICON_EXCLAMATION, boutons=[_(u"Ok"), ])
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Sauvegarde
        DB = GestionDB.DB()

        # Sauvegarde de la location
        listeDonnees = [    
            ("IDfamille", IDfamille),
            ("IDproduit", IDproduit),
            ("observations", observations),
            ("date_debut", date_debut),
            ("date_fin", date_fin),
            ("quantite", quantite),
            ]

        if self.IDlocation == None :
            listeDonnees.append(("date_saisie", datetime.date.today()))
            self.IDlocation = DB.ReqInsert("locations", listeDonnees)
        else:
            DB.ReqMAJ("locations", listeDonnees, "IDlocation", self.IDlocation)

        # Sauvegarde des prestations
        liste_prestations = self.ctrl_parametres.GetPageAvecCode("facturation").GetDonnees()["prestations"]

        listeID = []
        for track_prestation in liste_prestations :
            IDprestation = track_prestation.IDprestation

            listeDonnees = [
                ("IDcompte_payeur", self.ctrl_loueur.GetIDcomptePayeur()),
                ("date", track_prestation.date),
                ("categorie", "location"),
                ("label", track_prestation.label),
                ("montant_initial", track_prestation.montant),
                ("montant", track_prestation.montant),
                ("IDfamille", self.ctrl_loueur.GetIDfamille()),
                ("IDindividu", None),
                ("code_compta", None),
                ("tva", None),
                ("IDdonnee", self.IDlocation),
                ]

            if IDprestation == None :
                listeDonnees.append(("date_valeur", str(datetime.date.today())))
                IDprestation = DB.ReqInsert("prestations", listeDonnees)
            else:
                if track_prestation.dirty == True :
                    DB.ReqMAJ("prestations", listeDonnees, "IDprestation", IDprestation)
            listeID.append(IDprestation)

        # Suppression des prestations obsol�tes
        for IDprestation in self.liste_initiale_IDprestation :
            if IDprestation not in listeID :
                DB.ReqDEL("prestations", "IDprestation", IDprestation)
                DB.ReqDEL("ventilation", "IDprestation", IDprestation)

        # Sauvegarde du questionnaire
        self.ctrl_parametres.GetPageAvecCode("questionnaire").ctrl_questionnaire.Sauvegarde(DB=DB, IDdonnee=self.IDlocation)

        DB.Close()

        # Fermeture de la fen�tre
        self.EndModal(wx.ID_OK)

    def GetIDlocation(self):
        return self.IDlocation

    def Importation(self):
        """ Importation des donn�es """
        DB = GestionDB.DB()

        # Importation de la location
        req = """SELECT IDfamille, IDproduit, observations, date_debut, date_fin, quantite
        FROM locations WHERE IDlocation=%d;""" % self.IDlocation
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) == 0 :
            DB.Close()
            return
        IDfamille, IDproduit, observations, date_debut, date_fin, quantite = listeDonnees[0]

        # G�n�ralit�s
        self.ctrl_loueur.SetIDfamille(IDfamille)
        self.ctrl_produit.SetIDproduit(IDproduit)
        if observations == None :
            observations = ""
        self.ctrl_observations.SetValue(observations)

        # Date de d�but
        if date_debut != None :
            self.ctrl_date_debut.SetDate(datetime.datetime.strftime(UTILS_Dates.DateEngEnDateDDT(date_debut), "%Y-%m-%d"))
            self.ctrl_heure_debut.SetHeure(datetime.datetime.strftime(UTILS_Dates.DateEngEnDateDDT(date_debut), "%H:%M"))

        # Date de fin
        if date_fin != None :
            self.ctrl_date_fin.SetDate(datetime.datetime.strftime(UTILS_Dates.DateEngEnDateDDT(date_fin), "%Y-%m-%d"))
            self.ctrl_heure_fin.SetHeure(datetime.datetime.strftime(UTILS_Dates.DateEngEnDateDDT(date_fin), "%H:%M"))
            self.check_date_fin.SetValue(True)

        # Quantit�
        if quantite != None :
            self.ctrl_quantite.SetValue(quantite)

        # Importation des prestations
        req = """SELECT
        IDprestation, date, label, montant, IDfacture
        FROM prestations 
        WHERE categorie="location" and IDdonnee=%d;""" % self.IDlocation
        DB.ExecuterReq(req)
        listePrestations = DB.ResultatReq()
        DB.Close()

        liste_tracks_prestations = []
        for IDprestation, date, label, montant, IDfacture in listePrestations :
            date = UTILS_Dates.DateEngEnDateDD(date)
            dictPrestation = {
                "IDprestation" : IDprestation, "date" : date, "label" : label,
                "montant": montant, "IDfacture" : IDfacture,
                }
            track_prestation = OL_Locations_prestations.Track_prestation(dictPrestation)
            liste_tracks_prestations.append(track_prestation)
            self.liste_initiale_IDprestation.append(IDprestation)

        self.ctrl_parametres.GetPageAvecCode("facturation").SetDonnees({"prestations" : liste_tracks_prestations})






if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDlocation=1, IDfamille=1)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()


