import os,sys
from copy import deepcopy as dc
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)

from framework.analysis import analysis
from framework.fileReader import GetHistoFromSetOfFiles
from framework.functions import *
from ROOT.TMath import Sqrt as sqrt
from ROOT import *
from modules.puWeightProducer import puWeight_5TeV
from modules.PrefireCorr import PrefCorr5TeV
#from modules.GetBTagSF import BtagReader

### Channel to ints
class ch():
  eee  = 0
  mmm  = 1
  mee  = 2
  emm  = 3
chan = {ch.eee:'eee', ch.mmm:'mmm', ch.mee:'mee', ch.emm:'emm'}

### Levels to ints
class lev():
  lep      = 0
  met      = 1
  wpt      = 2
  m3l      = 3

level = {lev.lep:'lep', lev.met:'met', lev.wpt:'wpt', lev.m3l:'m3l'}

### Systematic uncertainties
class systematic():
  nom       = -1 # Nominal
  MuonEffUp = 0
  MuonEffDo = 1
  ElecEffUp = 2
  ElecEffDo = 3
  JESUp = 4
  JESDo = 5
  JERUp = 6
  JERDo = 7
  PUUp = 8
  PUDo = 9
  PrefireUp = 10
  PrefireDo = 11
systlabel = {systematic.nom:'', systematic.MuonEffUp:'MuonEffUp', systematic.MuonEffDo:'MuonEffDown', systematic.ElecEffUp:'ElecEffUp', systematic.ElecEffDo:'ElecEffDown', systematic.JESUp:'JESUp', systematic.JESDo:'JESDown', systematic.JERUp:'JERUp', systematic.JERDo:'JERDown'}
#systematic.PUUp:'PUUp', systematic.PUDo:'PUDown'}

### Datasets to ints
class datasets():
  SingleMuon = 0
  SingleElec = 1
  DoubleMuon = 2
  DoubleElec = 3
  MuonEG     = 4
dataset = {datasets.SingleElec:'HighEGJet', datasets.SingleMuon:'SingleMuon'}

################ Analysis
class wzanalysis(analysis):
  def init(self):
    # Load SF files
    if not self.isData:
      #self.LoadHisto('MuonIsoSF', basepath+'./inputs/MuonISO.root', 'NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta') # pt, abseta
      #self.LoadHisto('MuonIdSF',  basepath+'./inputs/MuonID.root',  'NUM_TightID_DEN_genTracks_pt_abseta') # pt, abseta
      #self.LoadHisto('ElecSF',    basepath+'./inputs/ElecTightCBid94X.root',  'EGamma_SF2D') # eta, pt
      self.LoadHisto('MuonIsoSF', basepath+'./inputs/MuonISO.root', 'NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta') # pt, abseta
      self.LoadHisto('MuonIdSF',  basepath+'./inputs/MuonID.root',  'NUM_TightID_DEN_genTracks_pt_abseta') # pt, abseta
      self.LoadHisto('RecoEB',    basepath+'./inputs/ElecReco_EB_30_100.root',  'g_scalefactors') # Barrel
      self.LoadHisto('RecoEE',    basepath+'./inputs/ElecReco_EE_30_100.root',  'g_scalefactors') # Endcap
      self.LoadHisto('ElecEB',    basepath+'./inputs/sf_tight_id.root',  'g_eff_ratio_pt_barrel') # Endcap
      self.LoadHisto('ElecEE',    basepath+'./inputs/sf_tight_id.root',  'g_eff_ratio_pt_endcap') # Endcap
      self.LoadHisto('ElecTrigEB',    basepath+'./inputs/ScaleFactors_PbPb_LooseWP_EB_Centr_0_100_HLTonly_preliminaryID.root',  'g_scalefactors') # Barrel
      self.LoadHisto('ElecTrigEE',    basepath+'./inputs/ScaleFactors_PbPb_LooseWP_EE_Centr_0_100_HLTonly_preliminaryID.root',  'g_scalefactors') # Endcap

      # Modules to have some weights in MC
      self.PUweight = puWeight_5TeV(self.tchain, False)
      self.PrefCorr = PrefCorr5TeV(False)

    # To apply b tagging SF
    #self.BtagSF   = BtagReader('DeepCSV', 'mujets', 'Medium', 2017)

    # Uncertainties
    self.doSyst = False if ('noSyst' in self.options or self.isData) else True
    self.doJECunc = True if 'JECunc'   in self.options else False
    self.jetptvar = 'Jet_pt_nom' if 'JetPtNom' in self.options else 'Jet_pt'
    self.metptvar = 'Met_pt_nom' if 'JetPtNom' in self.options else 'Met_pt'

    if self.doJECunc:
      systlabel[systematic.JESUp]   = 'JESUp'
      systlabel[systematic.JESDo]   = 'JESDown'
      systlabel[systematic.JERUp]   = 'JERUp'
      systlabel[systematic.JERDo]   = 'JERDown'

    self.resetObjects()

    # Sample name
    name = self.sampleName
    self.isDY = True if 'DY' in self.sampleName else False

    # It it's data, store dataset index
    self.sampleDataset = -1
    for i, dataName in dataset.items(): 
      if dataName == name: self.sampleDataset = i

    # Jet and lep pT
    self.JetPtCut  = 20
    self.LepPtCut  = 8
    self.Lep0PtCut = 20

  def resetObjects(self):
    self.selLeptons = []
    self.selJets = []
    self.pmet = TLorentzVector()
    if not self.isData and self.doSyst:
      self.selJetsJESUp = []
      self.selJetsJESDo = []
      self.selJetsJERUp = []
      self.selJetsJERDo = []
      self.pmetJESUp = TLorentzVector()
      self.pmetJESDo = TLorentzVector()
      self.pmetJERUp = TLorentzVector()
      self.pmetJERDo = TLorentzVector()

  def GetName(self, var, ichan, ilevel = '', isyst = ''):
    ''' Crafts the name for a histo '''
    if isinstance(ichan,  int): ichan  = chan[ichan]
    if isinstance(ilevel, int): ilevel = level[ilevel]
    if isinstance(isyst,  int): isyst  = systlabel[isyst]
    name = var + ('_' + ichan if ichan != '' else '') + ('_' + ilevel if ilevel != '' else '') + ('_'+isyst if isyst != '' else '')
    return name

  def NewHisto(self, var, chan, level, syst, nbins, bin0, binN):
    ''' Used to create the histos following a structure '''
    self.CreateTH1F(self.GetName(var, chan, level, syst), "", nbins, bin0, binN)
    self.obj[self.GetName(var, chan, level, syst)].Sumw2()

  def GetHisto(self, var, chan, level = '', syst = ''):
    ''' Get a given histo using the tthisto structure '''
    return self.obj[self.GetName(var, chan, level, syst)]

  def createHistos(self):
    ''' Create all the histos for the analysis '''
    ### Yields histos
    for key_chan in chan:
      ichan = chan[key_chan]
      for key_syst in systlabel.keys():
        if not self.doSyst and key_syst != systematic.nom: continue
        isyst = systlabel[key_syst]
        self.NewHisto('Yields',   ichan, '', isyst, 5, 0, 5)
        self.NewHisto('YieldsSS', ichan, '', isyst, 5, 0, 5)

    ### Analysis histos
    for key_chan in chan:
      ichan = chan[key_chan]
      for key_level in level:
        ilevel = level[key_level]
        if ichan == 'ElMu' and (ilevel == 'ZVeto' or ilevel == 'MET'): continue
        # Create histos for PDF and scale systematics
        for key_syst in systlabel.keys():
          if key_syst != systematic.nom and self.isData: continue
          if not self.doSyst and key_syst != systematic.nom: continue
            
          isyst = systlabel[key_syst]
          # Event
          self.NewHisto('HT',   ichan,ilevel,isyst, 80, 0, 400)
          self.NewHisto('HTmiss',   ichan,ilevel,isyst, 80, 0, 400)
          self.NewHisto('MET',  ichan,ilevel,isyst, 30, 0, 150)
          self.NewHisto('NJets',ichan,ilevel,isyst, 8 ,-0.5, 7.5)
          self.NewHisto('Btags',ichan,ilevel,isyst, 4 ,-0.5, 3.5)
          self.NewHisto('Vtx',  ichan,ilevel,isyst, 10, -0.5, 9.5)
          self.NewHisto('NBtagNJets', ichan,ilevel,isyst, 7, -0.5, 6.5)

          # Leptons
          self.NewHisto('mz',     ichan,ilevel,isyst, 60, 76, 106)
          self.NewHisto('m3l',    ichan,ilevel,isyst, 60, 50, 350)
          self.NewHisto('mtw',    ichan,ilevel,isyst, 30, 0, 150)
          self.NewHisto('LepWPt', ichan,ilevel,isyst, 24, 0, 120)
          self.NewHisto('LepWEta', ichan,ilevel,isyst, 50, -2.5, 2.5)
          self.NewHisto('LepWPhi', ichan,ilevel,isyst, 20, -1, 1)
          self.NewHisto('LepZ0Pt', ichan,ilevel,isyst, 24, 0, 120)
          self.NewHisto('LepZ0Eta', ichan,ilevel,isyst, 50, -2.5, 2.5)
          self.NewHisto('LepZ1Pt', ichan,ilevel,isyst, 24, 0, 120)
          self.NewHisto('LepZ1Eta', ichan,ilevel,isyst, 50, -2.5, 2.5)
          self.NewHisto('LepZ0Phi', ichan,ilevel,isyst, 20, -1, 1)
          self.NewHisto('LepZ1Phi', ichan,ilevel,isyst, 20, -1, 1)
          self.NewHisto('TrilepPt', ichan,ilevel,isyst, 40, 0, 200)
          self.NewHisto('ZPt', ichan,ilevel,isyst, 40, 0, 200)
          self.NewHisto('InvMass', ichan,ilevel,isyst, 60, 0, 300)
          self.NewHisto('DYMass',  ichan,ilevel,isyst, 200, 70, 110)
          self.NewHisto('MaxDeltaPhi',  ichan,ilevel,isyst, 20, 0, 1)

          # Jets
          self.NewHisto('Jet0Pt',   ichan,ilevel,isyst, 60, 0, 300)
          self.NewHisto('Jet1Pt',   ichan,ilevel,isyst, 50, 0, 250)
          self.NewHisto('JetAllPt', ichan,ilevel,isyst, 60, 0, 300)
          self.NewHisto('Jet0Eta',   ichan,ilevel,isyst, 50, -2.5, 2.5)
          self.NewHisto('Jet1Eta',   ichan,ilevel,isyst, 50, -2.5, 2.5)
          self.NewHisto('JetAllEta', ichan,ilevel,isyst, 50, -2.5, 2.5)
          self.NewHisto('Jet0Csv',   ichan,ilevel,isyst, 40, 0, 1)
          self.NewHisto('Jet1Csv',   ichan,ilevel,isyst, 40, 0, 1)
          self.NewHisto('JetAllCsv', ichan,ilevel,isyst, 40, 0, 1)
          self.NewHisto('Jet0DCsv',   ichan,ilevel,isyst, 40, 0, 1)
          self.NewHisto('Jet1DCsv',   ichan,ilevel,isyst, 40, 0, 1)
          self.NewHisto('JetAllDCsv', ichan,ilevel,isyst, 40, 0, 1)

  def FillHistograms(self, leptons, jets, pmet, ich, ilev, isys):
    ''' Fill all the histograms. Take the inputs from lepton list, jet list, pmet '''
    if not len(leptons) >= 3: return # Just in case
    self.SetWeight(isys)
    mz = InvMass(leptons[1],leptons[2])
    mtw = MT(leptons[0].p, pmet)
    m3l = InvMass(leptons)

    # Re-calculate the observables
    lep0  = leptons[0]; lep1 = leptons[1]
    l0pt  = lep0.Pt();  l1pt  = lep1.Pt()
    l0eta = lep0.Eta(); l1eta = lep1.Eta()
    l0phi = lep0.Phi(); l1phi = lep1.Phi()

    lW  = TLorentzVector(leptons[0].p)
    lZ0 = TLorentzVector(leptons[1].p)
    lZ1 = TLorentzVector(leptons[2].p)
    lWpt  = lW. Pt();  lWeta = lW .Eta();  lWphi = lW .Phi()
    lZ0pt = lZ0.Pt(); lZ0eta = lZ0.Eta(); lZ0phi = lZ0.Phi()
    lZ1pt = lZ1.Pt(); lZ1eta = lZ1.Eta(); lZ1phi = lZ1.Phi()
    
    maxdphi = max([lW.DeltaPhi(lZ0), lW.DeltaPhi(lZ1), lZ0.DeltaPhi(lZ1)])    
    tript   = (lW+lZ0+lZ1).Pt()
    zpt     = (lZ0+lZ1).Pt()
    htmiss  = tript
    dphi  = DeltaPhi(lep0, lep1)
    mll   = InvMass(lep0, lep1)
    dipt  = DiPt(lep0, lep1)
                     
    met = pmet.Pt()
    ht = 0; 
    for j in jets: ht += j.Pt()
    njet = len(jets)
    nbtag = GetNBtags(jets)
    
    if njet > 0:
      jet0 = jets[0]
      j0pt = jet0.Pt(); j0eta = jet0.Eta(); j0phi = jet0.Phi()
      j0csv = jet0.GetCSVv2(); j0deepcsv = jet0.GetDeepCSV()
      htmiss = (lW+lZ0+lZ1+TLorentzVector(jet0.P())).Pt()
    if njet > 1:
      jet1 = jets[1]
      j1pt = jet1.Pt(); j1eta = jet1.Eta(); j1phi = jet1.Phi()
      j1csv = jet1.GetCSVv2(); j1deepcsv = jet1.GetDeepCSV()
      htmiss = (lW+lZ0+lZ1+TLorentzVector(jet0.P())+TLorentzVector(jet1.P())).Pt()
    else:
      j0pt = -1; j0eta = -999; j0phi = -999;
      j0csv = -1; j0deepcsv = -1;
    
    ### Fill the histograms
    #if ich == ch.ElMu and ilev == lev.dilepton: print 'Syst = ', isys, ', weight = ', self.weight
    self.GetHisto('HT',   ich,ilev,isys).Fill(ht, self.weight)
    self.GetHisto('HTmiss',   ich,ilev,isys).Fill(htmiss, self.weight)
    self.GetHisto('MET',  ich,ilev,isys).Fill(met, self.weight)
    self.GetHisto('NJets',ich,ilev,isys).Fill(njet, self.weight)
    self.GetHisto('Btags',ich,ilev,isys).Fill(nbtag, self.weight)
    self.GetHisto('Vtx',  ich,ilev,isys).Fill(self.nvtx, self.weight)
    self.GetHisto("InvMass", ich, ilev, isys).Fill(mll, self.weight)
    self.GetHisto("mz",      ich, ilev, isys).Fill(mz, self.weight)
    self.GetHisto("mtw",     ich, ilev, isys).Fill(mtw, self.weight)
    self.GetHisto("m3l",     ich, ilev, isys).Fill(m3l, self.weight)

    if   njet == 0: nbtagnjetsnum = nbtag
    elif njet == 1: nbtagnjetsnum = nbtag + 1
    elif njet == 2: nbtagnjetsnum = nbtag + 3
    else          : nbtagnjetsnum = 6
    self.GetHisto('NBtagNJets', ich, ilev,isys).Fill(nbtagnjetsnum, self.weight)

    # Leptons
    self.GetHisto('LepWPt', ich,ilev,isys).Fill(lWpt, self.weight)
    self.GetHisto('LepZ0Pt', ich,ilev,isys).Fill(lZ0pt, self.weight)
    self.GetHisto('LepZ1Pt', ich,ilev,isys).Fill(lZ1pt, self.weight)
    self.GetHisto('LepWEta', ich,ilev,isys).Fill(lWeta, self.weight)
    self.GetHisto('LepZ0Eta', ich,ilev,isys).Fill(lZ0eta, self.weight)
    self.GetHisto('LepZ1Eta', ich,ilev,isys).Fill(lZ1eta, self.weight)
    self.GetHisto('LepWPhi', ich,ilev,isys).Fill(lWphi/3.141592, self.weight)
    self.GetHisto('LepZ0Phi', ich,ilev,isys).Fill(lZ0phi/3.141592, self.weight)
    self.GetHisto('LepZ1Phi', ich,ilev,isys).Fill(lZ1phi/3.141592, self.weight)
    self.GetHisto('TrilepPt', ich,ilev,isys).Fill(tript, self.weight)
    self.GetHisto('ZPt',      ich,ilev,isys).Fill(zpt, self.weight)

    self.GetHisto('MaxDeltaPhi',  ich,ilev,isys).Fill(maxdphi/3.141592, self.weight)


    self.GetHisto('InvMass', ich,ilev,isys).Fill(mll, self.weight)
    if mll > 70 and mll < 110: 
      self.GetHisto('DYMass',  ich,ilev,isys).Fill(mll, self.weight)

    # Jets
    if njet >= 1:
      self.GetHisto('Jet0Pt',   ich,ilev,isys).Fill(j0pt, self.weight)
      self.GetHisto('Jet0Eta',   ich,ilev,isys).Fill(j0eta, self.weight)
      self.GetHisto('Jet0Csv',   ich,ilev,isys).Fill(j0csv, self.weight)
      self.GetHisto('Jet0DCsv',   ich,ilev,isys).Fill(j0deepcsv, self.weight)

    if njet >= 2:
      self.GetHisto('Jet1Pt',   ich,ilev,isys).Fill(j1pt, self.weight)
      self.GetHisto('Jet1Eta',   ich,ilev,isys).Fill(j1eta, self.weight)
      self.GetHisto('Jet1Csv',   ich,ilev,isys).Fill(j1csv, self.weight)
      self.GetHisto('Jet1DCsv',   ich,ilev,isys).Fill(j1deepcsv, self.weight)

    for ijet in jets:
      self.GetHisto('JetAllPt', ich,ilev,isys).Fill(ijet.Pt(), self.weight)
      self.GetHisto('JetAllEta', ich,ilev,isys).Fill(ijet.Eta(), self.weight)
      self.GetHisto('JetAllCsv', ich,ilev,isys).Fill(ijet.GetCSVv2(), self.weight)
      self.GetHisto('JetAllDCsv', ich,ilev,isys).Fill(ijet.GetDeepCSV(), self.weight)

  def FillYieldsHistos(self, ich, ilev, isyst):
    ''' Fill histograms for yields '''
    self.SetWeight(isyst)
    self.GetHisto('Yields',   ich, '', isyst).Fill(ilev, self.weight)

  def FillAll(self, ich, ilev, isyst, leps, jets, pmet):
    ''' Fill histograms for a given variation, channel and level '''
    self.FillYieldsHistos(ich, ilev, isyst)
    self.FillHistograms(leps, jets, pmet, ich, ilev, isyst)

  def SetWeight(self, syst):
    ''' Sets the event weight according to the systematic variation '''
    # elec, muon, pu, trigger...
    if not isinstance(syst, int): print '[WARNING] Label ', syst, ' is not an integer...'
    self.weight = self.EventWeight
    if   syst == systematic.nom:       self.weight *= self.SFmuon * self.SFelec * self.PUSF * self.prefWeight
    elif syst == systematic.ElecEffUp: self.weight *= self.SFmuon * (self.SFelec + self.SFelecErr) * self.PUSF * self.prefWeight
    elif syst == systematic.ElecEffDo: self.weight *= self.SFmuon * (self.SFelec - self.SFelecErr) * self.PUSF * self.prefWeight
    elif syst == systematic.MuonEffUp: self.weight *= (self.SFmuon + self.SFmuonErr) * self.SFelec * self.PUSF * self.prefWeight
    elif syst == systematic.MuonEffDo: self.weight *= (self.SFmuon - self.SFmuonErr) * self.SFelec * self.PUSF * self.prefWeight
    elif syst == systematic.PUUp:      self.weight *= self.SFmuon * self.SFelec * self.PUUpSF * self.prefWeight
    elif syst == systematic.PUDo:      self.weight *= self.SFmuon * self.SFelec * self.PUDoSF * self.prefWeight
    elif syst == systematic.PrefireUp: self.weight *= self.SFmuon * self.SFelec * self.PUSF * self.prefWeightUp
    elif syst == systematic.PrefireDo: self.weight *= self.SFmuon * self.SFelec * self.PUSF * self.prefWeightDo


  def SetVariables(self, isyst):
    leps = self.selLeptons
    jets = self.selJets
    pmet = self.pmet
    if   isyst == systematic.nom: return leps, jets, pmet
    elif isyst == systematic.JESUp:
      jets = self.selJetsJESUp
      pmet = self.pmetJESUp
    elif isyst == systematic.JESDo:
      jets = self.selJetsJESDo
      pmet = self.pmetJESDo
    elif isyst == systematic.JERUp:
      jets = self.selJetsJERUp
      pmet = self.pmetJERUp
    elif isyst == systematic.JERDo:
      jets = self.selJetsJERDo
      pmet = self.pmetJERDo
    return leps, jets, pmet

  def insideLoop(self, t):
    self.resetObjects()

    ### Lepton selection
    ###########################################
    if not self.isData: nGenLep = t.nGenDressedLepton 

    ##### Muons
    for i in range(t.nMuon):
      p = TLorentzVector()
      p.SetPtEtaPhiM(t.Muon_pt[i], t.Muon_eta[i], t.Muon_phi[i], t.Muon_mass[i])
      charge = t.Muon_charge[i]
      # Tight ID
      if not t.Muon_mediumId[i]: continue
      # Tight ISO, RelIso04 < 0.15
      if not t.Muon_pfRelIso04_all[i] < 0.25: continue
      # Tight IP
      dxy = abs(t.Muon_dxy[i])
      dz  = abs(t.Muon_dz[i] )
      if dxy > 0.05 or dz > 0.1: continue
      # pT < 12 GeV, |eta| < 2.4
      if p.Pt() < 8 or abs(p.Eta()) > 2.4: continue
      self.selLeptons.append(lepton(p, charge, 13))
       
    ##### Electrons
    for i in range(t.nElectron):
      p = TLorentzVector()
      p.SetPtEtaPhiM(t.Electron_pt[i], t.Electron_eta[i], t.Electron_phi[i], t.Electron_mass[i])
      charge = t.Electron_charge[i]
      etaSC    = abs(p.Eta());
      dEtaSC   = t.Electron_deltaEtaSC[i]
      convVeto = t.Electron_convVeto[i]
      R9       = t.Electron_r9[i]
      # Tight cut-based Id
      if not t.Electron_cutBased[i] >= 2: continue # Loose
      if not convVeto: continue
      # Isolation (RelIso03) tight
      relIso03 = t.Electron_pfRelIso03_all[i]
      #if   etaSC <= 1.479 and relIso03 > 0.0361: continue
      #elif etaSC >  1.479 and relIso03 > 0.094:  continue
      # Tight IP
      dxy = abs(t.Electron_dxy[i])
      dz  = abs(t.Electron_dz[i] )
      if dxy > 0.05 or dz > 0.1: continue
      # pT > 12 GeV, |eta| < 2.4
      if p.Pt() < 12 or abs(p.Eta()) > 2.4: continue
      self.selLeptons.append(lepton(p, charge, 11))
    leps = self.selLeptons
    pts  = [lep.Pt() for lep in leps]
    self.selLeptons = [lep for _,lep in sorted(zip(pts,leps))]

    # Lepton SF
    self.SFelec = 1; self.SFmuon = 1; self.SFelecErr = 0; self. SFmuonErr = 0
    if not self.isData:
      for lep in self.selLeptons:
        if lep.IsMuon():
          sf, err = self.GetSFandErr('MuonIsoSF, MuonIdSF', lep.Pt(), TMath.Abs(lep.Eta()))
          self.SFmuon*=sf
          self.SFmuonErr+=err*err # stat + syst from TnP
          self.SFmuonErr+=0.005*0.005 # Iso phase space extrapolation
        else:
          elecsf = 'ElecEB' if lep.Eta() < 1.479 else 'ElecEE'
          recosf = 'RecoEB' if lep.Eta() < 1.479 else 'RecoEE'
          ssf, serr = self.GetSFfromTGraph(elecsf,lep.Pt())
          rsf, rerr = self.GetSFfromTGraph(recosf,lep.Pt())
          sf = (1./ssf)*rsf;
          if rerr > 0.05: rerr = 0.01 # XXX TEMPORARY CORRECTION TO AVOID WRONG SF UNCERTAINTIES
          if serr > 0.05: serr = 0.01 # XXX TEMPORARY CORRECTION TO AVOID WRONG SF UNCERTAINTIES
          self.SFelec    *= sf
          self.SFelecErr += serr*serr + rerr*rerr
      self.SFelecErr = sqrt(self.SFelecErr)
      self.SFmuonErr = sqrt(self.SFmuonErr)

    ### Jet selection
    ###########################################

    for i in range(t.nJet):
      p = TLorentzVector()
      jetpt = getattr(t, self.jetptvar)[i]
      p.SetPtEtaPhiM(jetpt, t.Jet_eta[i], t.Jet_phi[i], t.Jet_mass[i])
      csv = t.Jet_btagCSVV2[i]; deepcsv = t.Jet_btagDeepB[i]; deepflav = t.Jet_btagDeepFlavB[i]
      jid = t.Jet_jetId[i]
      flav = t.Jet_hadronFlavour[i] if not self.isData else -999999;
      # Jet ID > 1, tight Id
      if not jid > 1: continue
      # |eta| < 2.4 
      if abs(p.Eta()) > 2.4: continue
      j = jet(p, csv, flav, jid, deepcsv, deepflav)
      if csv >= 0.8484 : j.SetBtag() ### Misssing CSVv2 SFs !!!! 
      if not j.IsClean(self.selLeptons, 0.4): continue
      if p.Pt()      >= self.JetPtCut: self.selJets.append(j)
      if not self.isData and self.doSyst:
        if self.doJECunc:
          pJESUp = TLorentzVector(); pJERUp = TLorentzVector()
          pJESDo = TLorentzVector(); pJERDo = TLorentzVector()
          pJESUp.SetPtEtaPhiM(t.Jet_pt_jesTotalUp[i],   t.Jet_eta[i], t.Jet_phi[i], t.Jet_mass_jesTotalUp[i])
          pJESDo.SetPtEtaPhiM(t.Jet_pt_jesTotalDown[i], t.Jet_eta[i], t.Jet_phi[i], t.Jet_mass_jesTotalDown[i])
          pJERUp.SetPtEtaPhiM(t.Jet_pt_jerUp[i],        t.Jet_eta[i], t.Jet_phi[i], t.Jet_mass_jerUp[i])
          pJERDo.SetPtEtaPhiM(t.Jet_pt_jerDown[i],      t.Jet_eta[i], t.Jet_phi[i], t.Jet_mass_jerDown[i])
          jJESUp = jet(pJESUp, csv, flav, jid, deepcsv)
          jJESDo = jet(pJESDo, csv, flav, jid, deepcsv)
          jJERUp = jet(pJERUp, csv, flav, jid, deepcsv)
          jJERDo = jet(pJERDo, csv, flav, jid, deepcsv)
          if csv >= 0.8484:
            jJESUp.SetBtag()
            jJESDo.SetBtag()
            jJERUp.SetBtag()
            jJERDo.SetBtag()
          if pJESUp.Pt() >= self.JetPtCut: self.selJetsJESUp.append(jJESUp)
          if pJESDo.Pt() >= self.JetPtCut: self.selJetsJESDo.append(jJESDo)
          if pJERUp.Pt() >= self.JetPtCut: self.selJetsJERUp.append(jJERUp)
          if pJERDo.Pt() >= self.JetPtCut: self.selJetsJERDo.append(jJERDo)
    self.selJets = SortByPt(self.selJets)
    if not self.isData and self.doSyst:
      self.selJetsJESUp = SortByPt(self.selJetsJESUp)
      self.selJetsJESDo = SortByPt(self.selJetsJESDo)
      self.selJetsJERUp = SortByPt(self.selJetsJERUp)
      self.selJetsJERDo = SortByPt(self.selJetsJERDo)

    ##### MET
    #met = getattr(t, self.metptvar)
    #self.pmet.SetPtEtaPhiM(met, 0, t.MET_phi, 0)
    self.pmet.SetPtEtaPhiM(t.MET_pt, 0, t.MET_phi, 0)
    if not self.isData and self.doSyst:
      self.pmetJESUp.SetPtEtaPhiM(t.MET_pt_jesTotalUp,   0, t.MET_phi_jesTotalUp,   0) 
      self.pmetJESDo.SetPtEtaPhiM(t.MET_pt_jesTotalDown, 0, t.MET_phi_jesTotalDown, 0) 
      self.pmetJERUp.SetPtEtaPhiM(t.MET_pt_jerUp,        0, t.MET_phi_jerUp,        0) 
      self.pmetJERDo.SetPtEtaPhiM(t.MET_pt_jerDown,      0, t.MET_phi_jerDown,      0) 

    nJets = len(self.selJets)
    nBtag = GetNBtags(self.selJets)

    ### Set trilepton channel
    nLep = len(self.selLeptons)
    if nLep < 3: return
    l0 = self.selLeptons[0]
    l1 = self.selLeptons[1]
    l2 = self.selLeptons[2]
    totId = l0.GetPDGid() + l1.GetPDGid() + l2.GetPDGid()
    ich = -1
    if   totId == 33: ich = ch.eee
    elif totId == 35: ich = ch.mee
    elif totId == 37: ich = ch.emm
    elif totId == 39: ich = ch.mmm
    #if totId != 33 and totId != 37: return
    # lW, lZ1, lZ2
    mz = [CheckZpair(l0,l1), CheckZpair(l0,l2), CheckZpair(l1,l2)]
    if max(mz) == 0: return
    mzdif = [abs(x-91) for x in mz]
    minmzdif = min(mzdif)
    if minmzdif == 0: return # +++, --- 
    elif minmzdif == mzdif[0]:
      lZ1 = dc(l0); lZ2 = dc(l1); lW = dc(l2)
    elif minmzdif == mzdif[1]:
      lZ1 = dc(l0); lZ2 = dc(l2); lW = dc(l1)
    elif minmzdif == mzdif[2]:
      lZ1 = dc(l1); lZ2 = dc(l2); lW = dc(l0)
    zleps = [lZ1, lZ2]
    tleps = [lW, lZ1, lZ2]
    wpt = lW.Pt()
    m3l = (lW.P() + lZ1.P() + lZ2.P()).M()
    ### Trigger
    ###########################################
    trigger = {
     ch.eee:t.HLT_HIEle20_WPLoose_Gsf or t.HLT_HIEle20_Ele12_CaloIdL_TrackIdL_IsoVL_DZ,
     ch.mee:t.HLT_HIL3Mu20 or t.HLT_HIEle20_WPLoose_Gsf or t.HLT_HIEle20_Ele12_CaloIdL_TrackIdL_IsoVL_DZ,
     ch.emm:t.HLT_HIL3Mu20 or t.HLT_HIEle20_WPLoose_Gsf or t.HLT_HIL3DoubleMu0 or t.HLT_HIL3DoubleMu10,
     ch.mmm:t.HLT_HIL3Mu20 or t.HLT_HIL3DoubleMu0 or t.HLT_HIL3DoubleMu10,
    }
    passTrig = trigger[ich]

    ### Remove overlap events in datasets
    # In tt @ 5.02 TeV, 
    if self.isData:
      if   self.sampleDataset == datasets.SingleElec:
        if   ich == ch.eee: passTrig = trigger[ch.eee]
        elif ich == ch.mee: passTrig = trigger[ch.eee] 
        elif ich == ch.emm: passTrig = trigger[ch.eee] and not trigger[ch.mmm]
        else:               passTrig = False
      elif self.sampleDataset == datasets.SingleMuon:
        if   ich == ch.mee: passTrig = trigger[ch.mmm] and not trigger[ch.eee]
        elif ich == ch.emm: passTrig = trigger[ch.mmm]
        elif ich == ch.mmm: passTrig = trigger[ch.mmm]
        else:               passTrig = False
      #elif self.sampleDataset == datasets.DoubleMuon:
      #  if   ich == ch.mmm: passTrig = trigger[ch.mmm]
      #  elif ich == ch.emm: passTrig = t.HLT_HIL3DoubleMu0 or t.HLT_HIL3DoubleMu10
      #  elif ich == ch.mee: passTrig = False
      #  else:               passTrig = False

    ### Event weight and othe global variables
    ###########################################
    self.nvtx   = t.PV_npvs
    '''
    if not self.isData:
      self.PUSF   = t.puWeight
      self.PUUpSF = t.puWeightUp
      self.PUDoSF = t.puWeightDown
    else:
      self.PUSF   = 1; self.PUUpSF = 1; self.PUDoSF = 1
    '''
    self.PUSF   = 1; self.PUUpSF = 1; self.PUDoSF = 1

    self.prefWeight = 1; self.prefWeightUp = 1; self.prefWeightDo = 1
    if not self.isData:
      self.prefWeight   = self.PrefCorr.GetWeight(t)
      self.prefWeightUp = self.PrefCorr.GetWeightUp(t)
      self.prefWeightDo = self.PrefCorr.GetWeightDown(t)
 
    ### Event selection
    ###########################################
    self.SetWeight(systematic.nom)
    weight = self.weight

    if not passTrig: return
    if max([x.p.Pt() for x in tleps]) < 20: return
    if abs(InvMass(zleps) - 91.) > 15.: return
    
    for isyst in systlabel.keys():
      if not self.doSyst and isyst != systematic.nom: continue
      if self.isData and isyst != systematic.nom: continue
      leps, jets, pmet = self.SetVariables(isyst)
      nJets = len(jets)
      nBtag = GetNBtags(jets)
      leps = tleps

      self.FillAll(ich, lev.lep, isyst, leps, jets, pmet)
  
      if pmet.Pt() > 25: 
        self.FillAll(ich,lev.met,isyst,leps,jets,pmet)
      if wpt > 20: 
        self.FillAll(ich, lev.wpt, isyst, leps, jets, pmet)
      if m3l > 100:
	self.FillAll(ich, lev.m3l, isyst, leps, jets, pmet)
