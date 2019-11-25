import os,sys
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)

from framework.analysis import analysis
from framework.fileReader import GetHistoFromSetOfFiles
from framework.functions import *
from ROOT.TMath import Sqrt as sqrt
from ROOT import *
from modules.puWeightProducer import puWeight_5TeV
from modules.PrefireCorr import PrefCorr5TeV
from modules.GetBTagSF import BtagReader
from MuonTrigSFPbPb import GetMuonTrigSF, GetMuonTrigEff, GetMuonEff, GetMuonEffDimuon

ttnomname = 'TT'

### Channel to ints
class ch():
  ElMu = 0
  MuMu = 1
  ElEl = 2
  Muon = 3
  Elec = 4
chan = {ch.ElMu:'ElMu', ch.MuMu:'MuMu', ch.ElEl:'ElEl'}

### Levels to ints
class lev():
  dilepton = 0
  ZVeto    = 1
  MET      = 2
  jets2    = 3
  btag1    = 4
  ww       = 5
level = {lev.dilepton:'dilepton', lev.ZVeto:'ZVeto', lev.MET:'MET', lev.jets2:'2jets', lev.btag1:'1btag', lev.ww:'ww'}
invlevel = {'dilepton':lev.dilepton, 'ZVeto':lev.ZVeto, 'MET':lev.MET, '2jets':lev.jets2, '1btag':lev.btag1, 'ww':lev.ww}

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
  TrigEffUp = 10
  TrigEffDo = 11
  PrefireUp = 12
  PrefireDo = 13
  BtagUp = 14
  BtagDo = 15
  MisTagUp = 16
  MisTagDo = 17
  ISRUp = 18
  ISRDo = 19
  FSRUp = 20
  FSRDo = 21
#systlabel = {systematic.nom:'', systematic.MuonEffUp:'MuonEffUp', systematic.MuonEffDo:'MuonEffDown', systematic.ElecEffUp:'ElecEffUp', systematic.ElecEffDo:'ElecEffDown', systematic.JESUp:'JESUp', systematic.JESDo:'JESDown', systematic.JERUp:'JERUp', systematic.JERDo:'JERDown', systematic.PUUp:'PUUp', systematic.PUDo:'PUDown', systematic.TrigEffUp:'TrigEffUp', systematic.TrigEffDo:'TrigEffDown', systematic.PrefireUp:'PrefireUp', systematic.PrefireDo:'PrefireDown', systematic.BtagUp:'BtagUp', systematic.BtagDo:'BtagDown', systematic.MisTagUp:'MisTagUp', systematic.MisTagDo:'MisTagDown', systematic.ISRUp:'ISRUp', systematic.ISRDo:'ISRDown', systematic.FSRUp:'FSRUp', systematic.FSRDo:'FSRDown'}
systlabel = {systematic.nom:'', systematic.MuonEffUp:'MuonEffUp', systematic.MuonEffDo:'MuonEffDown', systematic.ElecEffUp:'ElecEffUp', systematic.ElecEffDo:'ElecEffDown', systematic.TrigEffUp:'TrigEffUp', systematic.TrigEffDo:'TrigEffDown', systematic.PrefireUp:'PrefireUp', systematic.PrefireDo:'PrefireDown', systematic.BtagUp:'BtagUp', systematic.BtagDo:'BtagDown', systematic.MisTagUp:'MisTagUp', systematic.MisTagDo:'MisTagDown'}

### Datasets to ints
class datasets():
  SingleMuon = 0
  SingleElec = 1
  DoubleMuon = 2
  DoubleElec = 3
  MuonEG     = 4
dataset = {datasets.SingleElec:'HighEGJet', datasets.SingleMuon:'SingleMuon', datasets.DoubleMuon:'DoubleMuon'}


def GetElecPt(pt, eta, ecorr = 1, isdata = False):
  # ecorr: correction factor [calibrated energy]/[miniAOD energy]
  fact = 1
  if abs(eta) < 1.479: #barrel
    fact = (1.016-0.0035) if isdata else 1.005
  else:      # endcap
    fact = (1.052-0.036) if isdata else 0.992
  return pt*fact/ecorr

tr = TRandom(500)
def GetElecPtSmear(pt, eta, isdata = False):
  if(isdata): return pt
  mass = 91.1876
  val = 1.786 if abs(eta) < 1.479 else 3.451
  sigma = val/mass
  smear = tr.Gaus(1, sigma)
  return pt*smear
 

################ Analysis
class tt5TeV(analysis):

  def GetTrigElecEff(self, pt, eta, d = 'num', sys = 0):
    sfname = 'ElecTrigE%s%s'%('E' if eta > 1.479 else 'B', d)
    eff, efferr = self.GetSFfromTGraph(sfname, pt)
    if   sys ==  1: return eff+efferr
    elif sys == -1: return eff-efferr
    else          : return eff

  def GetElecTrigSF(self, pt, eta, pt2 = -99, eta2 = -99, sys = 0):
    if pt2 == -99 and eta2 == -99: # Only one electron
      num = self.GetTrigElecEff(pt, eta, 'num', sys)
      den = self.GetTrigElecEff(pt, eta, 'den', sys)
      SF = num/den
      return SF
    else:
      geff = lambda e1,e2 : e1+e2-e1*e2
      n1   = self.GetTrigElecEff(pt , eta , 'num', sys)
      d1   = self.GetTrigElecEff(pt , eta , 'den', sys)
      n2   = self.GetTrigElecEff(pt2, eta2, 'num', sys)
      d2   = self.GetTrigElecEff(pt2, eta2, 'den', sys)
      SF    = geff(n1  ,n2  )/geff(d1  ,  d2)
      return SF

  def GetEMuTrigSF(self, ept, eeta, mpt, meta, sys = 0):
    geff = lambda e1,e2 : e1+e2-e1*e2
    ne   = self.GetTrigElecEff(ept , eeta , 'num', sys)
    de   = self.GetTrigElecEff(ept , eeta , 'den', sys)
    nm, dm = GetMuonTrigEff(mpt,  meta, sys);
    SF    = geff(ne, nm  )/geff(de, dm)
    return SF

  def init(self):
    # Load SF files
    if not self.isData:
      # Lepton and trigger SF
      self.LoadHisto('MuonIsoSF', basepath+'./inputs/MuonISO.root', 'NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta') # pt, abseta
      self.LoadHisto('MuonIdSF',  basepath+'./inputs/MuonID.root',  'NUM_TightID_DEN_genTracks_pt_abseta') # pt, abseta
      self.LoadHisto('RecoEB',    basepath+'./inputs/ElecReco_EB_30_100.root',  'g_scalefactors') # Barrel
      self.LoadHisto('RecoEE',    basepath+'./inputs/ElecReco_EE_30_100.root',  'g_scalefactors') # Endcap
      self.LoadHisto('ElecEB',    basepath+'./inputs/sf_tight_id.root',  'g_eff_ratio_pt_barrel') # Endcap loose/medium/tight
      self.LoadHisto('ElecEE',    basepath+'./inputs/sf_tight_id.root',  'g_eff_ratio_pt_endcap') # Endcap
      #self.LoadHisto('ElecTrigEB',    basepath+'./inputs/ScaleFactors_PbPb_LooseWP_EB_Centr_0_100_HLTonly_preliminaryID.root',  'g_scalefactors') # Barrel
      #self.LoadHisto('ElecTrigEE',    basepath+'./inputs/ScaleFactors_PbPb_LooseWP_EE_Centr_0_100_HLTonly_preliminaryID.root',  'g_scalefactors') # Endcap
      self.LoadHisto('ElecTrigEBnum',    basepath+'./inputs/eleTreeEff0_PbPb_LooseWP_EB_Centr_0_100_HLTOnly_Data.root',  'Graph') # Barrel data
      self.LoadHisto('ElecTrigEBden',    basepath+'./inputs/eleTreeEff0_PbPb_LooseWP_EB_Centr_0_100_HLTOnly_MC.root',    'Graph') # Barrel MC
      self.LoadHisto('ElecTrigEEnum',    basepath+'./inputs/eleTreeEff0_PbPb_LooseWP_EE_Centr_0_100_HLTOnly_Data.root',  'Graph') # Endcap data
      self.LoadHisto('ElecTrigEEden',    basepath+'./inputs/eleTreeEff0_PbPb_LooseWP_EE_Centr_0_100_HLTOnly_MC.root',    'Graph') # Endcap MC

      # Modules to have some weights in MC
      self.PUweight = puWeight_5TeV(self.tchain, self.index <= 0)
      self.PrefCorr = PrefCorr5TeV(self.index <= 0)

    # To apply b tagging SF
    self.BtagSF   = BtagReader('DeepCSV', 'mujets', 'Medium', 2017)

    # Uncertainties
    self.doSyst   = False if ('noSyst' in self.options or self.isData) else True
    self.doJECunc = True if 'JECunc'   in self.options else False
    self.doPU     = True if 'PUweight' in self.options else False
    self.doIFSR   = True if 'doIFSR'   in self.options and self.outname == 'TT' else False
    self.jetptvar   = 'Jet_pt_nom'   if 'JetPtNom' in self.options else 'Jet_pt'
    self.jetmassvar = 'Jet_mass_nom' if 'JetPtNom' in self.options else 'Jet_mass'
    self.metptvar   = 'MET_pt_nom'   if 'JetPtNom' in self.options else 'MET_pt'
    self.metphivar  = 'MET_phi_nom'  if 'JetPtNom' in self.options else 'MET_phi'

    if self.doPU: 
      systlabel[systematic.PUUp]   = 'PUUp'
      systlabel[systematic.PUDo]   = 'PUDown'
 
    if self.doJECunc:
      systlabel[systematic.JESUp]   = 'JESUp'
      systlabel[systematic.JESDo]   = 'JESDown'
      systlabel[systematic.JERUp]   = 'JERUp'
      systlabel[systematic.JERDo]   = 'JERDown'

    if self.doIFSR:
      systlabel[systematic.ISRDo]   = 'ISRDown'
      systlabel[systematic.ISRUp]   = 'ISRUp'
      systlabel[systematic.FSRDo]   = 'FSRDown'
      systlabel[systematic.FSRUp]   = 'FSRUp'

    # Objects for the analysis
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

    # Sample name
    name = self.outname#sampleName
    self.isTT = True if name[0:2] == 'TT' else False
    self.isTTnom = True if self.sampleName == ttnomname else False
    self.doTTbarSemilep = False
    if self.isTT and 'semi' in name or 'Semi' in name:
      self.doTTbarSemilep = True
      self.SetOutName("TTsemilep")
      if self.index <= 0: print 'Setting out name to TTsemilep...'
    self.isDY = True if 'DY' in self.sampleName else False

    # PDF and scale histos for TT sample
    if self.isTTnom and self.index <= 0:
      hSumPDF   = GetHistoFromSetOfFiles(self.GetFiles(), 'SumOfPDFweights')
      hSumScale = GetHistoFromSetOfFiles(self.GetFiles(), 'SumOfScaleWeights')
      self.AddToOutputs('SumOfPDFweights', hSumPDF)
      self.AddToOutputs('SumOfScaleWeights', hSumScale)
    
    # It it's data, store dataset index
    self.sampleDataset = -1
    for i, dataName in dataset.items(): 
      if dataName == name: self.sampleDataset = i

    # Jet and lep pT
    self.JetPtCut  = 25
    self.LepPtCut  = 12
    self.Lep0PtCut = 20
    self.metcut    = 30

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

  def GetHisto(self, var, chan, level = '', syst = ''):
    ''' Get a given histo using the tthisto structure '''
    return self.obj[self.GetName(var, chan, level, syst)]

  def createHistos(self):
    ''' Create all the histos for the analysis '''
    self.isTTnom = True if self.outname      == 'TT' else False
    self.isTT    = True if self.outname[0:2] == 'TT' else False
    self.isDY    = True if 'DY' in self.sampleName      else False

    self.NewHisto('PUWeights', '', '', '', 100,0,5)
    self.NewHisto('MET_ElEl_2jetsnomet', '', '', '', 30,0,150)
    self.NewHisto('MET_MuMu_2jetsnomet', '', '', '', 30,0,150)

    ### Yields histos
    if self.isTT: self.NewHisto('FiduEvents', '', '', '', 5,0,5)
    for key_chan in chan:
      ichan = chan[key_chan]
      for key_syst in systlabel.keys():
        if not self.doSyst and key_syst != systematic.nom: continue
        isyst = systlabel[key_syst]
        self.NewHisto('Yields',   ichan, '', isyst, 5, 0, 5)
        self.NewHisto('YieldsSS', ichan, '', isyst, 5, 0, 5)

    ### Histos for DY
    if self.isData or self.isDY:
      for key_chan in chan:
        ichan = chan[key_chan]
        for key_level in level:
          ilevel = level[key_level]
          if ilevel == lev.ww: continue
          if key_level != lev.ZVeto:
            self.NewHisto('DYHisto', ichan, ilevel, '', 60, 0, 300)
            if key_level != lev.MET: 
              self.NewHisto('DYHistoElMu', ichan, ilevel, '', 60, 0, 300)
        self.NewHisto('DYHisto',     ichan, 'eq1jet', '', 60, 0, 300)
        self.NewHisto('DYHistoElMu', ichan, 'eq1jet', '', 60, 0, 300)
        self.NewHisto('DYHisto',     ichan, 'eq2jet', '', 60, 0, 300)
        self.NewHisto('DYHistoElMu', ichan, 'eq2jet', '', 60, 0, 300)
        self.NewHisto('DYHisto',     ichan, 'geq3jet', '', 60, 0, 300)
        self.NewHisto('DYHistoElMu', ichan, 'geq3jet', '', 60, 0, 300)
        self.NewHisto('DYHisto',     ichan, '2btag', '', 60, 0, 300)
        self.NewHisto('DYHistoElMu', ichan, '2btag', '', 60, 0, 300)

    ### Analysis histos
    for key_chan in chan:
      ichan = chan[key_chan]
      for key_level in level:
        ilevel = level[key_level]
        if ichan == 'ElMu' and (ilevel == 'ZVeto' or ilevel == 'MET'): continue
        # Create histos for PDF and scale systematics
        if self.isTTnom:
          self.NewHisto('PDFweights',ichan,ilevel,'',33,0.5,33.5)
          self.NewHisto('ScaleWeights',ichan,ilevel,'',9,0.5,9.5)
        for key_syst in systlabel.keys():
          if key_syst != systematic.nom and self.isData: continue
          if not self.doSyst and key_syst != systematic.nom: continue
          if key_syst in [systematic.PUUp, systematic.PUDo, systematic.PrefireUp, systematic.PrefireDo, systematic.ISRUp, systematic.ISRDo, systematic.FSRUp, systematic.FSRDo, systematic.BtagDo, systematic.BtagUp]: continue
            
          isyst = systlabel[key_syst]
          # Event
          self.NewHisto('HT',   ichan,ilevel,isyst, 80, 0, 400)
          self.NewHisto('MET',  ichan,ilevel,isyst, 30, 0, 150)
          self.NewHisto('NJets',ichan,ilevel,isyst, 8 ,-0.5, 7.5)
          self.NewHisto('Btags',ichan,ilevel,isyst, 4 ,-0.5, 3.5)
          self.NewHisto('Vtx',  ichan,ilevel,isyst, 10, -0.5, 9.5)
          self.NewHisto('NBtagNJets', ichan,ilevel,isyst, 7, -0.5, 6.5)

          # Leptons
          self.NewHisto('Lep0Pt', ichan,ilevel,isyst, 24, 0, 120)
          self.NewHisto('Lep1Pt', ichan,ilevel,isyst, 24, 0, 120)
          self.NewHisto('Lep0Eta', ichan,ilevel,isyst, 50, -2.5, 2.5)
          self.NewHisto('Lep1Eta', ichan,ilevel,isyst, 50, -2.5, 2.5)
          self.NewHisto('Lep0Phi', ichan,ilevel,isyst, 20, -1, 1)
          self.NewHisto('Lep1Phi', ichan,ilevel,isyst, 20, -1, 1)
          self.NewHisto('DilepPt', ichan,ilevel,isyst, 40, 0, 200)
          self.NewHisto('InvMass', ichan,ilevel,isyst, 60, 0, 300)
          self.NewHisto('DYMass',  ichan,ilevel,isyst, 200, 70, 110)
          self.NewHisto('DYMassBB',  ichan,ilevel,isyst, 200, 70, 110)
          self.NewHisto('DYMassBE',  ichan,ilevel,isyst, 200, 70, 110)
          self.NewHisto('DYMassEB',  ichan,ilevel,isyst, 200, 70, 110)
          self.NewHisto('DYMassEE',  ichan,ilevel,isyst, 200, 70, 110)
          self.NewHisto('DeltaPhi',  ichan,ilevel,isyst, 20, 0, 1)
          if ichan == chan[ch.ElMu]:
            self.NewHisto('ElecEta', 'ElMu',ilevel,isyst, 50, -2.5, 2.5)
            self.NewHisto('MuonEta', 'ElMu',ilevel,isyst, 50, -2.5, 2.5)
            self.NewHisto('ElecPt', 'ElMu',ilevel,isyst, 24, 0, 120)
            self.NewHisto('MuonPt', 'ElMu',ilevel,isyst, 24, 0, 120)
            self.NewHisto('ElecPhi', 'ElMu',ilevel,isyst, 20, -1, 1)
            self.NewHisto('MuonPhi', 'ElMu',ilevel,isyst, 20, -1, 1)

          # Jets
          self.NewHisto('Jet0Pt',   ichan,ilevel,isyst, 60, 0, 300)
          self.NewHisto('Jet1Pt',   ichan,ilevel,isyst, 50, 0, 250)
          self.NewHisto('JetAllPt', ichan,ilevel,isyst, 60, 0, 300)
          self.NewHisto('Jet0Eta',   ichan,ilevel,isyst, 50, -2.5, 2.5)
          self.NewHisto('Jet1Eta',   ichan,ilevel,isyst, 50, -2.5, 2.5)
          #self.NewHisto('JetAllEta', ichan,ilevel,isyst, 50, -2.5, 2.5)
          #self.NewHisto('Jet0Csv',   ichan,ilevel,isyst, 40, 0, 1)
          #self.NewHisto('Jet1Csv',   ichan,ilevel,isyst, 40, 0, 1)
          #self.NewHisto('JetAllCsv', ichan,ilevel,isyst, 40, 0, 1)
          self.NewHisto('Jet0DCsv',   ichan,ilevel,isyst, 40, 0, 1)
          self.NewHisto('Jet1DCsv',   ichan,ilevel,isyst, 40, 0, 1)
          #self.NewHisto('JetAllDCsv', ichan,ilevel,isyst, 40, 0, 1)

  def FillHistograms(self, leptons, jets, pmet, ich, ilev, isys):
    ''' Fill all the histograms. Take the inputs from lepton list, jet list, pmet '''
    if self.SS: return               # Do not fill histograms for same-sign events
    if not len(leptons) >= 2: return # Just in case
    self.SetWeight(isys)

    # Re-calculate the observables
    lep0  = leptons[0]; lep1 = leptons[1]
    l0pt  = lep0.Pt();  l1pt  = lep1.Pt()
    l0eta = lep0.Eta(); l1eta = lep1.Eta()
    l0phi = lep0.Phi(); l1phi = lep1.Phi()
    dphi  = DeltaPhi(lep0, lep1)
    mll   = InvMass(lep0, lep1)
    dipt  = DiPt(lep0, lep1)
    mupt  = 0; elpt  = 0
    mueta = 0; eleta = 0
    muphi = 0; elphi = 0
    if ich == ch.ElMu:
      if lep0.IsMuon():
         mu = lep0
         el = lep1
      else:
        mu = lep1
        el = lep0
      elpt  = el.Pt();  mupt  = mu.Pt()
      eleta = el.Eta(); mueta = mu.Eta()
      elphi = el.Phi(); muphi = mu.Phi()
                     
    met = pmet.Pt()
    ht = 0; 
    for j in jets: ht += j.Pt()
    njet = len(jets)
    nbtag = self.GetNBtagJets(jets, isys)
    
    if njet > 0:
      jet0 = jets[0]
      j0pt = jet0.Pt(); j0eta = jet0.Eta(); j0phi = jet0.Phi()
      j0csv = jet0.GetCSVv2(); j0deepcsv = jet0.GetDeepCSV()
    if njet > 1:
      jet1 = jets[1]
      j1pt = jet1.Pt(); j1eta = jet1.Eta(); j1phi = jet1.Phi()
      j1csv = jet1.GetCSVv2(); j1deepcsv = jet1.GetDeepCSV()
    else:
      j0pt = -1; j0eta = -999; j0phi = -999;
      j0csv = -1; j0deepcsv = -1;
    
    ### Fill the histograms
    #if ich == ch.ElMu and ilev == lev.dilepton: print 'Syst = ', isys, ', weight = ', self.weight
    self.GetHisto('HT',   ich,ilev,isys).Fill(ht, self.weight)
    self.GetHisto('MET',  ich,ilev,isys).Fill(met, self.weight)
    self.GetHisto('NJets',ich,ilev,isys).Fill(njet, self.weight)
    self.GetHisto('Btags',ich,ilev,isys).Fill(nbtag, self.weight)
    self.GetHisto('Vtx',  ich,ilev,isys).Fill(self.nvtx, self.weight)
    self.GetHisto("InvMass", ich, ilev, isys).Fill(mll, self.weight)

    if   njet == 0: nbtagnjetsnum = 0
    elif njet == 1: nbtagnjetsnum = nbtag + 1
    elif njet == 2: nbtagnjetsnum = nbtag + 3
    else          : nbtagnjetsnum = 6
    self.GetHisto('NBtagNJets', ich, ilev,isys).Fill(nbtagnjetsnum, self.weight)

    # Leptons
    self.GetHisto('Lep0Pt', ich,ilev,isys).Fill(l0pt, self.weight)
    self.GetHisto('Lep1Pt', ich,ilev,isys).Fill(l1pt, self.weight)
    self.GetHisto('Lep0Eta', ich,ilev,isys).Fill(l0eta, self.weight)
    self.GetHisto('Lep1Eta', ich,ilev,isys).Fill(l1eta, self.weight)
    self.GetHisto('Lep0Phi', ich,ilev,isys).Fill(l0phi/3.141592, self.weight)
    self.GetHisto('Lep1Phi', ich,ilev,isys).Fill(l1phi/3.141592, self.weight)
    self.GetHisto('DilepPt', ich,ilev,isys).Fill(dipt, self.weight)
    self.GetHisto('DeltaPhi',  ich,ilev,isys).Fill(dphi/3.141592, self.weight)
    self.GetHisto('InvMass', ich,ilev,isys).Fill(mll, self.weight)
    if mll > 70 and mll < 110: 
      self.GetHisto('DYMass',  ich,ilev,isys).Fill(mll, self.weight)
      l0eta = abs(l0eta); l1eta = abs(l1eta)
      if ich == ch.ElEl:
        if   l0eta <= 1.479 and l1eta <= 1.479: self.GetHisto('DYMassBB',  ich,ilev,isys).Fill(mll, self.weight)
        elif l0eta <= 1.479 and l1eta  > 1.479: self.GetHisto('DYMassBE',  ich,ilev,isys).Fill(mll, self.weight)
        elif l0eta  > 1.479 and l1eta <= 1.479: self.GetHisto('DYMassEB',  ich,ilev,isys).Fill(mll, self.weight)
        elif l0eta  > 1.479 and l1eta  > 1.479: self.GetHisto('DYMassEE',  ich,ilev,isys).Fill(mll, self.weight)
    if ich == ch.ElMu:
      self.GetHisto('ElecEta', ich,ilev,isys).Fill(eleta, self.weight)
      self.GetHisto('ElecPt',  ich,ilev,isys).Fill(elpt, self.weight)
      self.GetHisto('ElecPhi', ich,ilev,isys).Fill(elphi, self.weight)
      self.GetHisto('MuonEta', ich,ilev,isys).Fill(mueta, self.weight)
      self.GetHisto('MuonPt',  ich,ilev,isys).Fill(mupt, self.weight)
      self.GetHisto('MuonPhi', ich,ilev,isys).Fill(muphi, self.weight)

    # Jets
    if njet >= 1:
      self.GetHisto('Jet0Pt',   ich,ilev,isys).Fill(j0pt, self.weight)
      self.GetHisto('Jet0Eta',   ich,ilev,isys).Fill(j0eta, self.weight)
      #self.GetHisto('Jet0Csv',   ich,ilev,isys).Fill(j0csv, self.weight)
      self.GetHisto('Jet0DCsv',   ich,ilev,isys).Fill(j0deepcsv, self.weight)

    if njet >= 2:
      self.GetHisto('Jet1Pt',   ich,ilev,isys).Fill(j1pt, self.weight)
      self.GetHisto('Jet1Eta',   ich,ilev,isys).Fill(j1eta, self.weight)
      #self.GetHisto('Jet1Csv',   ich,ilev,isys).Fill(j1csv, self.weight)
      self.GetHisto('Jet1DCsv',   ich,ilev,isys).Fill(j1deepcsv, self.weight)

    #for ijet in jets:
    #  self.GetHisto('JetAllPt', ich,ilev,isys).Fill(ijet.Pt(), self.weight)
    #  self.GetHisto('JetAllEta', ich,ilev,isys).Fill(ijet.Eta(), self.weight)
    #  self.GetHisto('JetAllCsv', ich,ilev,isys).Fill(ijet.GetCSVv2(), self.weight)
    #  self.GetHisto('JetAllDCsv', ich,ilev,isys).Fill(ijet.GetDeepCSV(), self.weight)

  def FillYieldsHistos(self, ich, ilev, isyst):
    ''' Fill histograms for yields. Also for SS events for the nonprompt estimate '''
    self.SetWeight(isyst)
    if not self.SS: self.GetHisto('Yields',   ich, '', isyst).Fill(ilev, self.weight)
    else          : self.GetHisto('YieldsSS', ich, '', isyst).Fill(ilev, self.weight)

  def FillDYHistos(self, leptons, ich, ilev):
    ''' Fill DY histos used for the R_out/in method for DY estimate '''
    if self.SS: return # Do not fill the histograms with same-sign events
    if ilev == lev.ZVeto: return
    mll   = InvMass(leptons[0], leptons[1])
    self.GetHisto('DYHisto', ich, ilev).Fill(mll, self.weight)

  def FillDYHistosElMu(self, leptons, ich, ilev):
    ''' Fill DY histos used for the R_out/in method for the emu channel '''
    if self.SS: return # Do not fill the histograms with same-sign events
    if ilev == lev.ZVeto or ilev == lev.MET: return
    mll = InvMass(leptons[0], leptons[1])
    self.GetHisto('DYHistoElMu', ich, ilev).Fill(mll, self.weight)

  def FillAll(self, ich, ilev, isyst, leps, jets, pmet):
    ''' Fill histograms for a given variation, channel and level '''
    self.FillYieldsHistos(ich, ilev, isyst)
    if isyst not in [systematic.PUUp, systematic.PUDo, systematic.PrefireUp, systematic.PrefireDo, systematic.ISRUp, systematic.ISRDo, systematic.FSRUp, systematic.FSRDo, systematic.BtagDo, systematic.BtagUp]:
      self.FillHistograms(leps, jets, pmet, ich, ilev, isyst)

  def FillLHEweights(self, t, ich, ilev):
    weight = self.weight
    for i in range(t.nLHEPdfWeight):   self.GetHisto("PDFweights",   ich, ilev, -1).Fill(i+1, t.LHEPdfWeight[i]*weight)
    for i in range(t.nLHEScaleWeight): self.GetHisto("ScaleWeights", ich, ilev, -1).Fill(i+1, t.LHEScaleWeight[i]*weight)

  def SetWeight(self, syst):
    ''' Sets the event weight according to the systematic variation '''
    # elec, muon, pu, trigger...
    #self.TrigSF = 1
    #self.prefWeight = 1; 
    if not isinstance(syst, int): print '[WARNING] Label ', syst, ' is not an integer...'
    self.weight = self.EventWeight
    if   syst == systematic.nom:       self.weight *= self.SFmuon * self.SFelec * self.PUSF * self.TrigSF * self.prefWeight
    elif syst == systematic.ElecEffUp: self.weight *= self.SFmuon * (self.SFelec + self.SFelecErr) * self.PUSF * self.TrigSF * self.prefWeight
    elif syst == systematic.ElecEffDo: self.weight *= self.SFmuon * (self.SFelec - self.SFelecErr) * self.PUSF * self.TrigSF * self.prefWeight
    elif syst == systematic.MuonEffUp: self.weight *= (self.SFmuon + self.SFmuonErr) * self.SFelec * self.PUSF * self.TrigSF * self.prefWeight
    elif syst == systematic.MuonEffDo: self.weight *= (self.SFmuon - self.SFmuonErr) * self.SFelec * self.PUSF * self.TrigSF * self.prefWeight
    elif syst == systematic.TrigEffUp: self.weight *= self.SFmuon * self.SFelec * self.PUSF * self.TrigSFUp * self.prefWeight
    elif syst == systematic.TrigEffDo: self.weight *= self.SFmuon * self.SFelec * self.PUSF * self.TrigSFDo * self.prefWeight
    elif syst == systematic.PUUp:      self.weight *= self.SFmuon * self.SFelec * self.PUUpSF * self.TrigSF * self.prefWeight
    elif syst == systematic.PUDo:      self.weight *= self.SFmuon * self.SFelec * self.PUDoSF * self.TrigSF * self.prefWeight
    elif syst == systematic.PrefireUp: self.weight *= self.SFmuon * self.SFelec * self.PUSF * self.TrigSF * self.prefWeightUp
    elif syst == systematic.PrefireDo: self.weight *= self.SFmuon * self.SFelec * self.PUSF * self.TrigSF * self.prefWeightDo
    elif syst == systematic.ISRUp    : self.weight *= self.SFmuon * self.SFelec * self.PUSF * self.TrigSF * self.prefWeight * self.isrUp
    elif syst == systematic.ISRDo    : self.weight *= self.SFmuon * self.SFelec * self.PUSF * self.TrigSF * self.prefWeight * self.isrDo
    elif syst == systematic.FSRUp    : self.weight *= self.SFmuon * self.SFelec * self.PUSF * self.TrigSF * self.prefWeight * self.fsrUp
    elif syst == systematic.FSRDo    : self.weight *= self.SFmuon * self.SFelec * self.PUSF * self.TrigSF * self.prefWeight * self.fsrDo
    else                             : self.weight *= self.SFmuon * self.SFelec * self.PUSF * self.TrigSF * self.prefWeight
    #if   syst == systematic.nom:
    #   print 'SFmuon = ', self.SFmuon
    #   print 'SFelec = ', self.SFelec 
    #   print 'PUSF   = ', self.PUSF 
    #   print 'TrigSF = ', self.TrigSF 
    #   print 'prefWe = ', self.prefWeight

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

  def GetNBtagJets(self, jets, isyst = 0):
    nbtag = 0
    systIndex = 0
    if   isyst == systematic.BtagUp   : systIndex =  1
    elif isyst == systematic.BtagDo   : systIndex = -1
    elif isyst == systematic.MisTagUp : systIndex =  3
    elif isyst == systematic.MisTagDo : systIndex = -3
    for jet in jets:
      pt = jet.Pt(); eta = jet.Eta()
      tagger = jet.GetDeepCSV(); flav = jet.GetFlav() if not self.isData else -999999
      if self.BtagSF.IsBtag(tagger, flav, pt, eta, systIndex): nbtag += 1
    return nbtag

  def insideLoop(self, t):
    self.resetObjects()

    ### Lepton selection
    ###########################################
    if not self.isData: nGenLep = t.nGenDressedLepton 
    if self.isTT and not self.doTTbarSemilep and  nGenLep < 2: return
    if self.doTTbarSemilep and  nGenLep >= 2: return
    if self.isTT:
      genLep = []
      for i in range(nGenLep):
        p = TLorentzVector()
        p.SetPtEtaPhiM(t.GenDressedLepton_pt[i], t.GenDressedLepton_eta[i], t.GenDressedLepton_phi[i], t.GenDressedLepton_mass[i])
        pdgid = abs(t.GenDressedLepton_pdgId[i])
        if p.Pt() < 12 or abs(p.Eta()) > 2.4: continue
        genLep.append(lepton(p, 0, pdgid))
      pts    = [lep.Pt() for lep in genLep]
      genLep = [lep for _,lep in sorted(zip(pts,genLep))]

      if len(genLep) >= 2:
        genChan = 0
        l0 = genLep[0]; l1 = genLep[1]
        totId = l0.GetPDGid() + l1.GetPDGid()
        if   totId == 24: genChan = ch.ElMu
        elif totId == 22: genChan = ch.ElEl
        elif totId == 26: genChan = ch.MuMu
        genMll = InvMass(l0, l1)
   
        genMET = t.GenMET_pt
        genJets = []
        ngenJet = 0; ngenBJet = 0
        for i in range(t.nGenJet):
          p = TLorentzVector()
          p.SetPtEtaPhiM(t.GenJet_pt[i], t.GenJet_eta[i], t.GenJet_phi[i], t.GenJet_mass[i])
          if p.Pt() < self.JetPtCut or abs(p.Eta()) > 2.4: continue
          pdgid = abs(t.GenJet_partonFlavour[i])
          j = jet(p)
          #if not j.IsClean(genLep, 0.4): continue
          genJets.append(j)
          ngenJet += 1
          if pdgid == 5: ngenBJet+=1
    
        # Fill fidu yields histo 
        if genMll >= 20 and genLep[0].Pt() >= self.Lep0PtCut:
          self.obj['FiduEvents'].Fill(lev.dilepton)
          if genChan == ch.ElEl or genChan == ch.MuMu:
            if abs(genMll - 90) > 15:
              self.obj['FiduEvents'].Fill(lev.ZVeto)
              if genMET > self.metcut:
                self.obj['FiduEvents'].Fill(lev.MET)
                if ngenJet >= 2:
                  self.obj['FiduEvents'].Fill(lev.jets2)
                  if ngenBJet >= 1: self.obj['FiduEvents'].Fill(lev.btag1)
          else:
            self.obj['FiduEvents'].Fill(lev.ZVeto)
            self.obj['FiduEvents'].Fill(lev.MET)
            if ngenJet >= 2:
              self.obj['FiduEvents'].Fill(lev.jets2)
              if ngenBJet >= 1: self.obj['FiduEvents'].Fill(lev.btag1)
    
    ##### Muons
    for i in range(t.nMuon):
      p = TLorentzVector()
      p.SetPtEtaPhiM(t.Muon_pt[i], t.Muon_eta[i], t.Muon_phi[i], t.Muon_mass[i])
      charge = t.Muon_charge[i]
      # Tight ID
      if not t.Muon_tightId[i]: continue
      #if not t.Muon_mediumId[i]: continue
      # Tight ISO, RelIso04 < 0.15
      if not t.Muon_pfRelIso04_all[i] < 0.15: continue
      # Tight IP
      dxy = abs(t.Muon_dxy[i])
      dz  = abs(t.Muon_dz[i] )
      if dxy > 0.02 or dz > 0.05: continue
      # pT < 12 GeV, |eta| < 2.4
      if p.Pt() < 12 or abs(p.Eta()) > 2.4: continue
      self.selLeptons.append(lepton(p, charge, 13))
       
    ##### Electrons
    for i in range(t.nElectron):
      p = TLorentzVector()
      pt  = t.Electron_pt[i]
      eta = t.Electron_eta[i]
      ecorr = t.Electron_eCorr[i] if not self.isData else 1
      ptcorr = GetElecPt(pt, eta, ecorr, self.isData)
      ptcorr = GetElecPtSmear(ptcorr, eta, self.isData)
      p.SetPtEtaPhiM(ptcorr, eta, t.Electron_phi[i], t.Electron_mass[i])
      charge = t.Electron_charge[i]
      etaSC    = abs(p.Eta());
      dEtaSC   = t.Electron_deltaEtaSC[i]
      convVeto = t.Electron_convVeto[i]
      R9       = t.Electron_r9[i]
      # Tight cut-based Id
      if not t.Electron_cutBased[i] >= 4: continue # 4 Tightcut-based Id
      if not convVeto: continue
      # Isolation (RelIso03) tight --> Included in nanoAOD cutbased bit!!
      relIso03 = t.Electron_pfRelIso03_all[i]
      if   etaSC <= 1.479 and relIso03 > 0.0361: continue
      elif etaSC >  1.479 and relIso03 > 0.094:  continue
      # Tight IP
      dxy = abs(t.Electron_dxy[i])
      dz  = abs(t.Electron_dz[i] )
      if dxy > 0.02 or dz > 0.05: continue
      # pT > 12 GeV, |eta| < 2.4
      if p.Pt() < 12 or abs(p.Eta()) > 2.4: continue
      self.selLeptons.append(lepton(p, charge, 11))
    leps = self.selLeptons
    pts  = [lep.Pt() for lep in leps]
    self.selLeptons = [lep for _,lep in sorted(zip(pts,leps))]
    self.selLeptons.reverse()

    # Lepton SF
    self.SFelec = 1; self.SFmuon = 1; self.SFelecErr = 0; self. SFmuonErr = 0
    self.TrigSF = 1; self.TrigSFerr = 0; self.TrigSFUp = 1; self.TrigSFDo = 1;
    if not self.isData:
      for lep in self.selLeptons:
        if lep.IsMuon():
          #sf, err = self.GetSFandErr('MuonIsoSF, MuonIdSF', lep.Pt(), TMath.Abs(lep.Eta()))
          #self.SFmuon*=sf
          #self.SFmuonErr+=err*err # stat + syst from TnP
          #self.SFmuonErr+=0.005*0.005 # Iso phase space extrapolation
          self.SFmuon = GetMuonEff(lep.Pt(), lep.Eta())
          SFmuonUp = GetMuonEff(lep.Pt(), lep.Eta(),  1)
          SFmuonDo = GetMuonEff(lep.Pt(), lep.Eta(), -1)
          self.SFmuonErr = (abs(SFmuonUp - self.SFmuon) + abs(SFmuonDo - self.SFmuon))/2
        else:
          #sf, err = self.GetSFandErr('ElecSF', lep.Eta(), lep.Pt())
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
      #self.SFmuonErr = sqrt(self.SFmuonErr)
      #self.SFmuon = 1

    ### Jet selection
    ###########################################

    for i in range(t.nJet):
      p = TLorentzVector()
      jetpt   = getattr(t, self.jetptvar)[i]
      jetmass = getattr(t, self.jetmassvar)[i]
      p.SetPtEtaPhiM(jetpt, t.Jet_eta[i], t.Jet_phi[i], jetmass)
      csv = t.Jet_btagCSVV2[i]; deepcsv = t.Jet_btagDeepB[i]; deepflav = t.Jet_btagDeepFlavB[i]
      jid = t.Jet_jetId[i]
      flav = t.Jet_hadronFlavour[i] if not self.isData else -999999;
      # Jet ID > 1, tight Id
      if not jid > 1: continue
      # |eta| < 2.4 
      if abs(p.Eta()) > 2.4: continue
      j = jet(p, csv, flav, jid, deepcsv, deepflav)
      #if csv >= 0.8484 : j.SetBtag() ### Misssing CSVv2 SFs !!!! 
      if not j.IsClean(self.selLeptons, 0.4): continue
      if p.Pt()      >= self.JetPtCut: self.selJets.append(j)
      if not self.isData and self.doSyst and self.doJECunc:
        pJESUp = TLorentzVector(); pJERUp = TLorentzVector(); pJESDo = TLorentzVector(); pJERDo = TLorentzVector()
        pJESUp.SetPtEtaPhiM(t.Jet_pt_jesTotalUp[i],   t.Jet_eta[i], t.Jet_phi[i], t.Jet_mass_jesTotalUp[i])
        pJESDo.SetPtEtaPhiM(t.Jet_pt_jesTotalDown[i], t.Jet_eta[i], t.Jet_phi[i], t.Jet_mass_jesTotalDown[i])
        pJERUp.SetPtEtaPhiM(t.Jet_pt_jerUp[i],        t.Jet_eta[i], t.Jet_phi[i], t.Jet_mass_jerUp[i])
        pJERDo.SetPtEtaPhiM(t.Jet_pt_jerDown[i],      t.Jet_eta[i], t.Jet_phi[i], t.Jet_mass_jerDown[i])
        jJESUp = jet(pJESUp, csv, flav, jid, deepcsv, deepflav)
        jJESDo = jet(pJESDo, csv, flav, jid, deepcsv, deepflav)
        jJERUp = jet(pJERUp, csv, flav, jid, deepcsv, deepflav)
        jJERDo = jet(pJERDo, csv, flav, jid, deepcsv, deepflav)
        if pJESUp.Pt() >= self.JetPtCut: self.selJetsJESUp.append(jJESUp)
        if pJESDo.Pt() >= self.JetPtCut: self.selJetsJESDo.append(jJESDo)
        if pJERUp.Pt() >= self.JetPtCut: self.selJetsJERUp.append(jJERUp)
        if pJERDo.Pt() >= self.JetPtCut: self.selJetsJERDo.append(jJERDo)
    self.selJets = SortByPt(self.selJets)
    if not self.isData and self.doSyst and self.doJECunc:
      self.selJetsJESUp = SortByPt(self.selJetsJESUp)
      self.selJetsJESDo = SortByPt(self.selJetsJESDo)
      self.selJetsJERUp = SortByPt(self.selJetsJERUp)
      self.selJetsJERDo = SortByPt(self.selJetsJERDo)

    ##### MET
    #self.pmet.SetPtEtaPhiE(t.MET_pt, 0, t.MET_phi, 0)
    met    = getattr(t, self.metptvar)
    metphi = getattr(t, self.metphivar)
    self.pmet.SetPtEtaPhiM(met, 0, metphi, 0)
    if not self.isData and self.doSyst and self.doJECunc:
      self.pmetJESUp.SetPtEtaPhiM(t.MET_pt_jesTotalUp,   0, t.MET_phi_jesTotalUp,   0) 
      self.pmetJESDo.SetPtEtaPhiM(t.MET_pt_jesTotalDown, 0, t.MET_phi_jesTotalDown, 0) 
      self.pmetJERUp.SetPtEtaPhiM(t.MET_pt_jerUp,        0, t.MET_phi_jerUp,        0) 
      self.pmetJERDo.SetPtEtaPhiM(t.MET_pt_jerDown,      0, t.MET_phi_jerDown,      0) 

    nJets = len(self.selJets)
    nBtag = self.GetNBtagJets(self.selJets)

    ### Set dilepton channel
    nLep = len(self.selLeptons)
    if nLep < 2: return
    l0 = self.selLeptons[0]
    l1 = self.selLeptons[1]
    totId = l0.GetPDGid() + l1.GetPDGid()
    ich = -1
    if   totId == 24: ich = ch.ElMu
    elif totId == 22: ich = ch.ElEl
    elif totId == 26: ich = ch.MuMu
    
    ### Trigger
    ###########################################
    trigger = {
     ch.Elec:t.HLT_HIEle20_WPLoose_Gsf,
     ch.Muon:t.HLT_HIL3Mu20,
     ch.ElMu:t.HLT_HIL3Mu20 or t.HLT_HIEle20_WPLoose_Gsf, #t.HLT_HIL3Mu20 or t.HLT_HIEle20_WPLoose_Gsf,
     ch.ElEl:t.HLT_HIEle20_WPLoose_Gsf,
     ch.MuMu:t.HLT_HIL3Mu20# or t.HLT_HIL3DoubleMu0
    }
    passTrig = trigger[ich]

    # TrigerSF
    if not self.isData:
      if   ich == ch.MuMu:
        self.TrigSF, self.TrigSFerr = GetMuonTrigSF(l0.Pt(), l0.Eta(), l1.Pt(), l1.Eta() )
        self.TrigSFUp = self.TrigSF + self.TrigSFerr 
        self.TrigSFDo = self.TrigSF - self.TrigSFerr 
      elif ich == ch.Muon:
        self.TrigSF, self.TrigSFerr = GetMuonTrigSF(mu.Pt(), mu.Eta() )
        self.TrigSFUp = self.TrigSF + self.TrigSFerr 
        self.TrigSFDo = self.TrigSF - self.TrigSFerr 
      elif ich == ch.Elec:
        self.TrigSF   = self.GetElecTrigSF(el.pt(), el.eta(), sys =  0)
        self.TrigSFUp = self.GetElecTrigSF(el.pt(), el.eta(), sys =  1)
        self.TrigSFDo = self.GetElecTrigSF(el.pt(), el.eta(), sys = -1)
      elif ich == ch.ElEl:
        self.TrigSF   = self.GetElecTrigSF(l0.Pt(), l0.Eta(), l1.Pt(), l1.Eta(), 0)
        self.TrigSFUp = self.GetElecTrigSF(l0.Pt(), l0.Eta(), l1.Pt(), l1.Eta(), 1)
        self.TrigSFDo = self.GetElecTrigSF(l0.Pt(), l0.Eta(), l1.Pt(), l1.Eta(),-1)
      elif ich == ch.ElMu:
        mu = l0 if l0.IsMuon() else l1
        el = l1 if l0.IsMuon() else l0
        self.TrigSF   = self.GetEMuTrigSF(el.Pt(), el.Eta(), mu.Pt(), mu.Eta(), sys =  0)
        self.TrigSFUp = self.GetEMuTrigSF(el.Pt(), el.Eta(), mu.Pt(), mu.Eta(), sys =  1)
        self.TrigSFDo = self.GetEMuTrigSF(el.Pt(), el.Eta(), mu.Pt(), mu.Eta(), sys = -1)

    ### Remove overlap events in datasets
    # In tt @ 5.02 TeV, 
    if self.isData:
      if   self.sampleDataset == datasets.SingleElec:
        if   ich == ch.ElEl: passTrig = trigger[ch.ElEl]
        elif ich == ch.ElMu: passTrig = trigger[ch.Elec] and not trigger[ch.Muon]
        else:                passTrig = False
      elif self.sampleDataset == datasets.SingleMuon:
        if   ich == ch.MuMu: passTrig = trigger[ch.MuMu]
        elif ich == ch.ElMu: passTrig = trigger[ch.ElMu]
        else:                passTrig = False
      elif self.sampleDataset == datasets.DoubleMuon:
        if   ich == ch.MuMu: passTrig = trigger[ich]
        else:                passTrig = False

    ### Event weight and othe global variables
    ###########################################
    self.nvtx   = t.PV_npvs
    self.PUSF   = 1; self.PUUpSF = 1; self.PUDoSF = 1
    #if not self.isData and self.doPU:
    #  self.PUSF   = t.puWeight
    #  self.PUUpSF = t.puWeightUp
    #  self.PUDoSF = t.puWeightDown
    #if not self.isData:
    #  self.PUSF   = self.PUweight.GetWeight(t)
    #  self.PUUpSF = self.PUweight.GetWeightUp(t)
    #  self.PUDoSF = self.PUweight.GetWeightDown(t)
    self.obj['PUWeights'].Fill(self.PUSF)
 
    self.prefWeight = 1; self.prefWeightUp = 1; self.prefWeightDo = 1
    if not self.isData:
      self.prefWeight   = self.PrefCorr.GetWeight(t)
      self.prefWeightUp = self.PrefCorr.GetWeightUp(t)
      self.prefWeightDo = self.PrefCorr.GetWeightDown(t)

    self.fsrUp = 1; self.fsrDo = 1; self.isrUp = 1; self.isrDo = 1
    if self.doIFSR:
      self.isrDo = t.PSWeight[0]
      self.fsrDo = t.PSWeight[1]
      self.isrUp = t.PSWeight[2]
      self.fsrUp = t.PSWeight[3]
 
    ### Event selection
    ###########################################
    self.SetWeight(systematic.nom)
    weight = self.weight
    
    if not passTrig: return
    self.SS = l0.charge*l1.charge > 0
    for isyst in systlabel.keys():
      if not self.doSyst and isyst != systematic.nom: continue
      if self.isData and isyst != systematic.nom: continue
      leps, jets, pmet = self.SetVariables(isyst)
      nJets = len(jets)
      nBtag = self.GetNBtagJets(jets, isyst)
      if not len(leps) >= 2: continue
      l0 = leps[0]; l1 = leps[1]

      ### Dilepton pair
      if l0.Pt() < 20: continue
      if InvMass(l0,l1) < 20: continue
      self.FillAll(ich, lev.dilepton, isyst, leps, jets, pmet)
      if self.isTTnom and isyst == systematic.nom: self.FillLHEweights(t, ich, lev.dilepton)

      # >> Fill the DY histograms
      if (self.isData or self.isDY) and isyst == systematic.nom:
        self.FillDYHistos(self.selLeptons, ich, lev.dilepton)
        if self.pmet.Pt() > self.metcut:
          self.FillDYHistos(self.selLeptons, ich, lev.MET)
          if   nJets == 1: self.FillDYHistos(self.selLeptons, ich, 'eq1jet')
          elif nJets == 2: self.FillDYHistos(self.selLeptons, ich, 'eq2jet')
          elif nJets >= 3: self.FillDYHistos(self.selLeptons, ich, 'geq3jet')
          if nJets >= 2:
            self.FillDYHistos(self.selLeptons, ich, lev.jets2)
            if nBtag >= 1:
              self.FillDYHistos(self.selLeptons, ich, lev.btag1)
              if nBtag >= 2:
                self.FillDYHistos(self.selLeptons, ich, '2btag')
        if   nJets == 1: self.FillDYHistosElMu(self.selLeptons, ich, 'eq1jet')
        elif nJets == 2: self.FillDYHistosElMu(self.selLeptons, ich, 'eq2jet')
        elif nJets >= 3: self.FillDYHistosElMu(self.selLeptons, ich, 'geq3jet')
        if nJets >= 2:
          self.FillDYHistosElMu(self.selLeptons, ich, lev.jets2)
          if nBtag >= 1:
            self.FillDYHistosElMu(self.selLeptons, ich, lev.btag1)
            if nBtag >= 2:
              self.FillDYHistosElMu(self.selLeptons, ich, '2btag')

      ### WW selec
      if (l1.p+l0.p).Pt() > 20 and nJets == 0 and pmet.Pt() > 25:
        self.FillAll(ich, lev.ww, isyst, leps, jets, pmet)
  
      ### Z Veto + MET cut
      if ich == ch.MuMu or ich == ch.ElEl:
        if abs(InvMass(l0,l1) - 91) < 15: continue
        self.FillAll(ich, lev.ZVeto, isyst, leps, jets, pmet)
        if self.isTTnom and isyst == systematic.nom: self.FillLHEweights(t, ich, lev.ZVeto)
        if nJets >= 2 and isyst == systematic.nom:
          # Fill MET histos for events with 2 jets 
          self.GetHisto('MET', ich, '2jetsnomet', -1).Fill(pmet.Pt(), self.weight)
        if pmet.Pt() < self.metcut: continue
        self.FillAll(ich,lev.MET,isyst,leps,jets,pmet)
        if self.isTTnom and isyst == systematic.nom: self.FillLHEweights(t, ich, lev.MET)

      ### 2 jets
      if nJets < 2: continue
      self.FillAll(ich, lev.jets2, isyst, leps, jets, pmet)
      if self.isTTnom and isyst == systematic.nom: self.FillLHEweights(t, ich, lev.jets2)

      ### 1 b-tag, CSVv2 Medium
      if nBtag < 1: continue 
      self.FillAll(ich, lev.btag1, isyst, leps, jets, pmet)
      if self.isTTnom and isyst == systematic.nom: self.FillLHEweights(t, ich, lev.btag1)
