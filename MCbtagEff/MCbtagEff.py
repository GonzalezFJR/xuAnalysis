import os,sys
sys.path.append(os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/')
from framework.analysis import analysis
import framework.functions as fun
from array import array
from ROOT import TLorentzVector

class MCbtagEff(analysis):

  def GetName(self, year, tagger, wpname, tipo = 'B'):
    if isinstance(year, int): year = "%i"%year
    name = "BtagSF%s_%s%s_%s"%(tipo, tagger, wpname, year);
    return name

  def GetHisto(self, year, tagger, wpname, tipo = 'B'):
    return self.obj[self.GetName(year, tagger, wpname, tipo)]

  def init(self):
    year = 0
    if   '2018' in self.options: year = '2018'
    elif '2017' in self.options: year = '2017'
    elif '2016' in self.options: year = '2016'

    self.nptbins = 6;
    self.netabins = 4;
    self.pt = array('f',[20, 40, 60, 80, 100, 120, 150])
    self.eta = array('f',[0, 0.6, 1.2, 1.8, 2.4])
    #self.years = ['2016', '2017', '2018']
    self.years = [year]
    self.taggers = ['CSVv2', 'DeepCSV', 'DFlav']
    self.tipos = ['B', 'C', 'L']
    self.CSVtag = 'CSVv2' 
    self.deepCSVtag = 'DeepCSV'
    self.dflavtag   = 'DFlav'
    self.wptag      = ['L', 'M', 'T']
    # https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation102X
    self.wps = {
      '2016':{
        'CSVv2':{
          'L' : 0.5426, # 
          'M': 0.8484,
          'T': 0.9535,
        },
        'DeepCSV':{
          'L': 0.2217,
          'M': 0.6321,
          'T': 0.8953,
        },
        'DeepFlav':{
          'L': 0.0614,
          'M': 0.3093,
          'T': 0.7221,
        }
      },
      '2017':{
        'CSVv2':{
          'L': 0.5803,
          'M': 0.8838,
          'T': 0.9693,
        },
        'DeepCSV':{
          'L': 0.1522,
          'M': 0.4941,
          'T': 0.8001,
        },
        'DFlav':{
          'L': 0.0521,
          'M': 0.3033,
          'T': 0.7489,
        }
      },
      '2018':{
        'CSVv2':{
          'L': 0.5803, 
          'M': 0.8838,
          'T': 0.9693,
        },
        'DeepCSV':{
          'L': 0.1241,
          'M': 0.4184,
          'T': 0.7527,
        },
        'DFlav':{
          'L': 0.0494,
          'M': 0.2770,
          'T': 0.7264,
        }
      }
    }

    for year in self.years:
      for tag in self.taggers:
        for tip in self.tipos:
          for wp in self.wptag + ['D']:
            name = self.GetName(year, tag, wp, tip)
            self.CreateTH2F(name, name, self.nptbins, self.pt, self.netabins, self.eta)
          
          if isinstance(year, int): year = "%i"%year
          nameS = '%s%s_%s'%(tag,tip,year)
          self.CreateTH1F(nameS, nameS, 100, 0, 1)

  def insideLoop(self,t):
    # Simple analysis: lets draw the invariant mass of two muons
    # Lets require medium Id for the muons
    selMuon = []; 
    for i in range(t.nJet):
      p = TLorentzVector()
      p.SetPtEtaPhiM(t.Jet_pt[i], t.Jet_eta[i], t.Jet_phi[i], t.Jet_mass[i])
      csv = t.Jet_btagCSVV2[i]; deepcsv = t.Jet_btagDeepB[i]; dflav = t.Jet_btagDeepFlavB[i]
      jindex = i
      jid = t.Jet_jetId[i]
      flav = t.Jet_hadronFlavour[i] if not self.isData else -99;

      # Jet ID > 1, tight Id
      pt = p.Pt(); eta = abs(p.Eta())
      if not jid >= 1: continue
      if eta > 2.4 or pt < 20: continue

      if flav == 5: # is a b!!
        tip = 'B'
        for year in self.years:
          for tag, tval in zip([self.CSVtag, self.deepCSVtag, self.dflavtag], [csv, deepcsv, dflav]):
            nameS = '%s%s_%s'%(tag,tip,year)
            self.obj[nameS].Fill(tval)
            self.GetHisto(year, tag, 'D', tip).Fill(pt, eta)
            for wp in self.wptag:
              val = self.wps[year][tag][wp]
              if tval > val: self.GetHisto(year, tag, wp, tip).Fill(pt,eta)

      elif flav == 4: # is a c!!
        tip = 'C'
        for year in self.years:
          for tag, tval in zip([self.CSVtag, self.deepCSVtag, self.dflavtag], [csv, deepcsv, dflav]):
            nameS = '%s%s_%s'%(tag,tip,year)
            self.obj[nameS].Fill(tval)
            self.GetHisto(year, tag, 'D', tip).Fill(pt, eta)
            for wp in self.wptag:
              val = self.wps[year][tag][wp]
              if tval > val: self.GetHisto(year, tag, wp, tip).Fill(pt,eta)

      else: # light
        tip = 'L'
        for year in self.years:
          for tag, tval in zip([self.CSVtag, self.deepCSVtag, self.dflavtag], [csv, deepcsv, dflav]):
            nameS = '%s%s_%s'%(tag,tip,year)
            self.obj[nameS].Fill(tval)
            self.GetHisto(year, tag, 'D', tip).Fill(pt, eta)
            for wp in self.wptag:
              val = self.wps[year][tag][wp]
              if tval > val: self.GetHisto(year, tag, wp, tip).Fill(pt,eta)

