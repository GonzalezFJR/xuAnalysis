import os,sys
sys.path.append(os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/')
from framework.analysis import analysis
import framework.functions as fun
from array import array
from ROOT import TLorentzVector

class MCbtagEff(analysis):

  def GetName(self, year, wpname, isMis = False):
    s = '%s_%s'%(year, wpname)
    if isMis: s = 'Mis'+s
    return s

  def GetHisto(self, year, wpname, coef = 'Num', isMis = False):
    return self.obj[self.GetName(year, wpname, isMis)]

  def init(self):
    self.nptbins = 6;
    self.netabins = 4;
    self.pt = array('f',[20, 40, 60, 80, 100, 120, 150])
    self.eta = array('f',[0, 0.6, 1.2, 1.8, 2.4])
    self.years = ['2016', '2017', '2018']
    self.taggers = ['CSVv2L', 'CSVv2M', 'CSVv2T', 'DeepCSVL', 'DeepCSVM', 'DeepCSVT', 'DFlavL', 'DFlavM', 'DFlavT']
    self.CSVtag = 'CSVv2' 
    self.deepCSVtag = 'DeepCSV'
    self.dflavtag   = 'DFlav'
    self.wptag      = ['L', 'M', 'T']
    self.wps = {
      '2016':{
        'CSVv2L': 0.5426, # 
        'CSVv2M': 0.8484,
        'CSVv2T': 0.9535,
        'DeepCSVL': 0.2217,
        'DeepCSVM': 0.6321,
        'DeepCSVT': 0.8953,
        'DFlavL': 0.0614,
        'DFlavM': 0.3093,
        'DFlavT': 0.7221,
      },
      '2017':{
        'CSVv2L': 0.5803,
        'CSVv2M': 0.8838,
        'CSVv2T': 0.9693,
        'DeepCSVL': 0.1522,
        'DeepCSVM': 0.4941,
        'DeepCSVT': 0.8001,
        'DFlavL': 0.0521,
        'DFlavM': 0.3033,
        'DFlavT': 0.7489,
      },
      '2018':{
       'CSVv2L': 0.5803, 
       'CSVv2M': 0.8838,
       'CSVv2T': 0.9693,
       'DeepCSVL': 0.1241,
       'DeepCSVM': 0.4184,
       'DeepCSVT': 0.7527,
       'DFlavL': 0.0494,
       'DFlavM': 0.2770,
       'DFlavT': 0.7264,
      }
    }

    for year in self.years:
      for wp in self.taggers + ['CSVv2D', 'DeepCSVD', 'DFlavD']:
        self.CreateTH2F(self.GetName(year, wp, 0), self.GetName(year, wp, 0), self.nptbins, self.pt, self.netabins, self.eta)
        self.CreateTH2F(self.GetName(year, wp, 1), self.GetName(year, wp, 1), self.nptbins, self.pt, self.netabins, self.eta)

      self.CreateTH1F('CSVv2_'      +year, 'CSVv2_'+year,    100, 0, 1)
      self.CreateTH1F('DeepCSV_'    +year, 'DeepCSV_'+year,  100, 0, 1)
      self.CreateTH1F('DFlav_'      +year,    'DFlav_'+year, 100, 0, 1)
      self.CreateTH1F('MisCSVv2_'   +year, 'MisCSVv2_'+year,    100, 0, 1)
      self.CreateTH1F('MisDeepCSV_' +year, 'MisDeepCSV_'+year,  100, 0, 1)
      self.CreateTH1F('MisDFlav_'   +year, 'MisDFlav_'+year, 100, 0, 1)

  def insideLoop(self,t):
    # Simple analysis: lets draw the invariant mass of two muons
    # Lets require medium Id for the muons
    selMuon = []; 
    for i in range(t.nJet):
      p = TLorentzVector()
      p.SetPtEtaPhiM(t.Jet_pt_nom[i], t.Jet_eta[i], t.Jet_phi[i], t.Jet_mass[i])
      csv = t.Jet_btagCSVV2[i]; deepcsv = t.Jet_btagDeepB[i]; dflav = t.Jet_btagDeepFlavB[i]
      jindex = i
      jid = t.Jet_jetId[i]
      flav = t.Jet_hadronFlavour[i] if not self.isData else -99;

      # Jet ID > 1, tight Id
      pt = p.Pt(); eta = abs(p.Eta())
      if not jid > 1: continue
      if eta > 2.4: continue

      if flav == 5: # is a b!!
        for year in self.years:
          for tagger, tval in zip([self.CSVtag, self.deepCSVtag, self.dflavtag], [csv, deepcsv, dflav]):
            self.obj[tagger + '_' + year].Fill(tval,1)
            tad = tagger+'D'
            self.GetHisto(year, tad, 0).Fill(pt, eta,1)
            for wp in self.wptag:
              tag = tagger+wp
              val = self.wps[year][tag]
              if tval > val: self.GetHisto(year, tag, 0).Fill(pt,eta,1)

      else: # is not a b !!
        for year in self.years:
          for tagger, tval in zip([self.CSVtag, self.deepCSVtag, self.dflavtag], [csv, deepcsv, dflav]):
            self.obj['Mis' + tagger + '_' + year].Fill(tval,1)
            tad = tagger+'D'
            self.GetHisto(year, tad, 1).Fill(pt, eta,1)
            for wp in self.wptag:
              tag = tagger+wp
              val = self.wps[year][tag]
              if tval > val: self.GetHisto(year, tag, 1).Fill(pt,eta,1)

