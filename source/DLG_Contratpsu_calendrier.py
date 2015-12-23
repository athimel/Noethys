#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


from UTILS_Traduction import _
import wx
import OL_Contratspsu_previsions



class Panel(wx.Panel):
    def __init__(self, parent, clsbase=None):
        wx.Panel.__init__(self, parent, id=-1, name="panel_calendrier", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.clsbase = clsbase
        self.MAJ_effectuee = False

        # Pr�visions
        self.staticbox_previsions_staticbox = wx.StaticBox(self, -1, _(u"Pr�sences pr�visionnelles"))
        self.listviewAvecFooter = OL_Contratspsu_previsions.ListviewAvecFooter(self, kwargs={"clsbase" : clsbase})
        self.ctrl_previsions = self.listviewAvecFooter.GetListview()
        self.ctrl_recherche = OL_Contratspsu_previsions.CTRL_Outils(self, listview=self.ctrl_previsions, afficherCocher=True)
        if self.parent.GetName() == "notebook" :
            self.ctrl_recherche.SetBackgroundColour(self.parent.GetThemeBackgroundColour())

        self.bouton_previsions_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_previsions_modifier = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_previsions_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        self.bouton_previsions_apercu = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Apercu.png", wx.BITMAP_TYPE_ANY))
        self.bouton_previsions_imprimer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Imprimante.png", wx.BITMAP_TYPE_ANY))

        # Absences
        self.staticbox_absences_staticbox = wx.StaticBox(self, -1, _(u"Absences RTT"))
        self.label_absences_prevues = wx.StaticText(self, -1, _(u"Pr�vues :"))
        self.ctrl_absences_prevues = wx.SpinCtrl(self, -1, "0", size=(50, -1), min=0, max=99999)
        self.label_absences_prises = wx.StaticText(self, -1, _(u"Prises :"))
        self.ctrl_absences_prises = wx.TextCtrl(self, -1, "0", size=(40, -1), style=wx.TE_RIGHT)
        self.ctrl_absences_prises.Enable(False)
        self.label_absences_solde = wx.StaticText(self, -1, _(u"Restantes :"))
        self.ctrl_absences_solde = wx.TextCtrl(self, -1, "0", size=(40, -1), style=wx.TE_RIGHT)
        self.ctrl_absences_solde.Enable(False)

        # Options
        self.staticbox_options_staticbox = wx.StaticBox(self, -1, _(u"Options"))
        self.label_arrondi = wx.StaticText(self, -1, _(u"Arrondi :"))
        self.liste_arrondi_type = [(None, _(u"Aucun")), ("tranche_horaire", _(u"Tranche horaire")), ("duree", _(u"Dur�e"))]
        self.liste_arrondi_delta = [(10, _(u"10 min")), (15, _(u"15 min")), (30, _(u"30 min")), (60, _(u"60 min"))]
        self.ctrl_arrondi_type = wx.Choice(self, -1, choices=[label for code, label in self.liste_arrondi_type])
        self.ctrl_arrondi_delta = wx.Choice(self, -1, choices=[label for code, label in self.liste_arrondi_delta])

        self.__set_properties()
        self.__do_layout()

        # Binds
        self.Bind(wx.EVT_BUTTON, self.ctrl_previsions.Ajouter, self.bouton_previsions_ajouter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_previsions.Modifier, self.bouton_previsions_modifier)
        self.Bind(wx.EVT_BUTTON, self.ctrl_previsions.Supprimer, self.bouton_previsions_supprimer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_previsions.Apercu, self.bouton_previsions_apercu)
        self.Bind(wx.EVT_BUTTON, self.ctrl_previsions.Imprimer, self.bouton_previsions_imprimer)
        self.Bind(wx.EVT_TEXT, self.OnChangeAbsencesPrevues, self.ctrl_absences_prevues)
        self.Bind(wx.EVT_CHOICE, self.OnChoixArrondi, self.ctrl_arrondi_type)
        self.Bind(wx.EVT_CHOICE, self.OnChoixArrondi, self.ctrl_arrondi_delta)

        # Init
        self.OnChangeAbsencesPrevues()
        self.ctrl_arrondi_type.SetSelection(0)
        self.ctrl_arrondi_delta.SetSelection(0)
        # self.OnChoixArrondi()
        self.ctrl_arrondi_delta.Enable(self.ctrl_arrondi_type.GetSelection() != 0)

    def __set_properties(self):
        self.bouton_previsions_ajouter.SetToolTipString(_(u"Cliquez ici pour ajouter une consommation"))
        self.bouton_previsions_modifier.SetToolTipString(_(u"Cliquez ici pour modifier la consommation s�lectionn�e"))
        self.bouton_previsions_supprimer.SetToolTipString(_(u"Cliquez ici pour supprimer la consommation s�lectionn�e"))
        self.bouton_previsions_apercu.SetToolTipString(_(u"Cliquez ici pour afficher un aper�u avant impression de la liste"))
        self.bouton_previsions_imprimer.SetToolTipString(_(u"Cliquez ici pour imprimer la liste"))
        self.ctrl_absences_prevues.SetToolTipString(_(u"Saisissez ici le nombre d'heures d'absences pr�vues (RTT)"))
        self.ctrl_arrondi_type.SetToolTipString(_(u"S�lectionnez un type d'arrondi"))
        self.ctrl_arrondi_delta.SetToolTipString(_(u"S�lectionnez le deltade l'arrondi"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        # Pr�visions
        staticbox_previsions = wx.StaticBoxSizer(self.staticbox_previsions_staticbox, wx.VERTICAL)
        grid_sizer_previsions = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)

        grid_sizer_previsions.Add(self.listviewAvecFooter, 1, wx.EXPAND, 0)

        grid_sizer_boutons_previsions = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons_previsions.Add(self.bouton_previsions_ajouter, 0, 0, 0)
        grid_sizer_boutons_previsions.Add(self.bouton_previsions_modifier, 0, 0, 0)
        grid_sizer_boutons_previsions.Add(self.bouton_previsions_supprimer, 0, 0, 0)
        grid_sizer_boutons_previsions.Add( (5, 5), 0, 0, 0)
        grid_sizer_boutons_previsions.Add(self.bouton_previsions_apercu, 0, 0, 0)
        grid_sizer_boutons_previsions.Add(self.bouton_previsions_imprimer, 0, 0, 0)

        grid_sizer_previsions.Add(grid_sizer_boutons_previsions, 1, wx.EXPAND, 0)

        grid_sizer_previsions.Add(self.ctrl_recherche, 1, wx.EXPAND, 0)

        grid_sizer_previsions.AddGrowableRow(0)
        grid_sizer_previsions.AddGrowableCol(0)
        staticbox_previsions.Add(grid_sizer_previsions, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_previsions, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        grid_sizer_bas = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)

        # Absences
        staticbox_absences = wx.StaticBoxSizer(self.staticbox_absences_staticbox, wx.VERTICAL)
        grid_sizer_absences = wx.FlexGridSizer(rows=1, cols=8, vgap=5, hgap=5)
        grid_sizer_absences.Add(self.label_absences_prevues, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_absences.Add(self.ctrl_absences_prevues, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_absences.Add( (5, 5), 0, 0, 0)
        grid_sizer_absences.Add(self.label_absences_prises, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_absences.Add(self.ctrl_absences_prises, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_absences.Add( (5, 5), 0, 0, 0)
        grid_sizer_absences.Add(self.label_absences_solde, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_absences.Add(self.ctrl_absences_solde, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_absences.AddGrowableCol(1)
        grid_sizer_absences.AddGrowableCol(4)
        grid_sizer_absences.AddGrowableCol(7)
        staticbox_absences.Add(grid_sizer_absences, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_bas.Add(staticbox_absences, 1, wx.EXPAND, 0)

        # Options
        staticbox_options = wx.StaticBoxSizer(self.staticbox_options_staticbox, wx.VERTICAL)
        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=8, vgap=5, hgap=5)
        grid_sizer_options.Add(self.label_arrondi, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_arrondi_type, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_arrondi_delta, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 0)
        staticbox_options.Add(grid_sizer_options, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_bas.Add(staticbox_options, 1, wx.EXPAND, 0)

        grid_sizer_bas.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_bas, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)

    def OnChangeAbsencesPrevues(self, event=None):
        prises = int(self.ctrl_absences_prises.GetValue())
        solde = int(self.ctrl_absences_prevues.GetValue()) - prises
        self.ctrl_absences_solde.SetValue(str(solde))

    def OnChoixArrondi(self, event=None):
        self.ctrl_arrondi_delta.Enable(self.ctrl_arrondi_type.GetSelection() != 0)
        arrondi_type = self.GetArrondiType()
        arrondi_delta = self.GetArrondiDelta()
        self.clsbase.SetValeur("arrondi_type", arrondi_type)
        self.clsbase.SetValeur("arrondi_delta", arrondi_delta)
        self.ctrl_previsions.MAJtracks()
        self.clsbase.SetValeur("tracks_previsions", self.ctrl_previsions.GetTracks())
        self.clsbase.Calculer()

    def GetArrondiType(self):
        return self.liste_arrondi_type[self.ctrl_arrondi_type.GetSelection()][0]

    def GetArrondiDelta(self):
        return self.liste_arrondi_delta[self.ctrl_arrondi_delta.GetSelection()][0]

    def SetArrondiType(self, arrondi_type=None):
        index = 0
        for code, label in self.liste_arrondi_type :
            if code == arrondi_type :
                self.ctrl_arrondi_type.SetSelection(index)
            index += 1
        self.ctrl_arrondi_delta.Enable(self.ctrl_arrondi_type.GetSelection() != 0)

    def SetArrondiDelta(self, arrondi_delta=10):
        index = 0
        for code, label in self.liste_arrondi_delta :
            if code == arrondi_delta :
                self.ctrl_arrondi_delta.SetSelection(index)
            index += 1

    def Validation(self):
        if self.clsbase.Calculer(mode_test=True) == False :
            return False

        return True

    def Sauvegarde(self):
        self.clsbase.SetValeur("tracks_previsions", self.ctrl_previsions.GetTracks())
        self.clsbase.SetValeur("nbre_absences_prevues", int(self.ctrl_absences_prevues.GetValue()))
        self.clsbase.SetValeur("nbre_absences_prises", int(self.ctrl_absences_prises.GetValue()))
        self.clsbase.SetValeur("nbre_absences_solde", int(self.ctrl_absences_solde.GetValue()))
        self.clsbase.SetValeur("arrondi_type", self.GetArrondiType())
        self.clsbase.SetValeur("arrondi_delta", self.GetArrondiDelta())

    def MAJ(self):
        self.clsbase.Calculer()

        if self.MAJ_effectuee == False :

            # Pr�visions
            self.ctrl_previsions.IDunite_prevision = self.clsbase.GetValeur("IDunite_prevision")
            self.ctrl_previsions.SetTracks(self.clsbase.GetValeur("tracks_previsions", []))

            # Absences
            nbre_absences_prevues = self.clsbase.GetValeur("nbre_absences_prevues")
            if nbre_absences_prevues != None :
                self.ctrl_absences_prevues.SetValue(nbre_absences_prevues)
            nbre_absences_prises = self.clsbase.GetValeur("nbre_absences_prises")
            if nbre_absences_prises != None :
                self.ctrl_absences_prises.SetValue(nbre_absences_prises)
            self.OnChangeAbsencesPrevues()

            # Options
            arrondi_type = self.clsbase.GetValeur("arrondi_type", "duree")
            self.SetArrondiType(arrondi_type)
            arrondi_delta = self.clsbase.GetValeur("arrondi_delta", 30)
            self.SetArrondiDelta(arrondi_delta)

        self.MAJ_effectuee = True


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        from DLG_Saisie_contratpsu import Base
        self.clsbase = Base(IDcontrat=None)
        self.ctrl = Panel(panel, clsbase=self.clsbase)
        self.bouton_test = wx.Button(panel, -1, "Test")
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.bouton_test, 0, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest, self.bouton_test)

    def OnBoutonTest(self, event):
        self.clsbase.CalculerTotaux()



if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(700, 500))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()