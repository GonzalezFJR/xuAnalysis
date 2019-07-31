import os,sys
#import ROOT
from ROOT import TH1F, TH1, TFile, TCanvas, TPad, THStack, TLatex, TLegend, TGaxis
from ROOT import kRed, kOrange, kBlue, kTeal, kGreen, kGray, kAzure, kPink, kCyan, kBlack
from ROOT import gPad, gROOT
from ROOT.TMath import Sqrt as sqrt
average = lambda x: sum(x)/len(x)
gROOT.SetBatch(1)
sys.path.append(os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/')

from ttbar.ttanalysis import ch, chan, lev, level, dataset, datasets, systematic, systlabel  
from plotter.TopHistoReader import TopHistoReader

#################################################################################################
### Histo saver
#################################################################################################

class HistoSaver:
 ''' Class to save histograms from different process and prepare a .root file 
     to use with the Higgs Combine tool
 '''

 def SetPath(self, p):
  if not p.endswith('/'): p += '/'
  if p == '/': p = './'
  self.path = p
  self.t.SetPath(self.path)

 def SetOutputDir(self, d):
  self.outdir = d
  if not self.outdir.endswith('/'): self.outdir += '/'

 def SetOutName(self, n):
  if n == '': n = 'histos'
  self.outname = n

 def GetOutFileName(self):
  return self.outdir + self.outname + '.root'

 def AddSystematic(self, *s):
  if len(s) == 1: s = s[0] 
  if isinstance(s, list) or isinstance(s, tuple): 
    for e in s: self.AddSystematic(e)
  else:
    self.syst.append(s)

 def SetVar(self, var):
  self.var = var

 def SetChan(self, chan):
   self.chan = chan
  
 def SetLevel(self, ilevel):
   self.level = ilevel

 def SetHistoName(self, h = ''):
   self.histoName = h

 def SetLumi(self, lumi):
   self.lumi = lumi
   self.t.SetLumi(self.lumi)

 def SetVarChanLev(self, var, ch, ilev):
  self.SetVar(var)
  self.SetChan(ch)
  self.SetLevel(ilev)

 def SetRebin(self, r = 1):
  self.rebin = r
  self.t.SetRebin(self.rebin)

 def AddProcess(self, prName, files = ''):
  if isinstance(prName, dict):
    self.dpr = prName
  elif isinstance(prName, list):
    for pr,f in zip(prName, files): self.dpr[pr] = f
  else: self.dpr[prName] = files

 def AddData(self, files = ''):
  self.dataFiles = files

 def AddHisto(self, h, prName, systname = ''):
  hOut = prName if systname == '' else prName + '_' + systname
  h.SetName(hOut)
  self.histos.append(h)

 def LoadHisto(self, fname, process, syst = '',hname = '', ):
  if fname in self.dpr.keys(): fname = self.dpr[fname]
  if hname == '': hname = self.GetHistoName()
  if syst != '':
    if self.t.IsHisto(fname, hname+'_'+syst): 
      self.LoadHisto(fname, process+'_'+syst, hname = hname+'_'+syst)
      return
    else:
      if self.t.IsHisto(fname, hname+'_'+syst+'Up'):   self.LoadHisto(fname, process+'_'+syst+'Up', hname = hname+'_'+syst+'Up')
      if self.t.IsHisto(fname, hname+'_'+syst+'Down'): self.LoadHisto(fname, process+'_'+syst+'Down', hname = hname+'_'+syst+'Down')
      return
  h = self.t.GetNamedHisto(hname, fname, self.rebin)
  self.AddHisto(h, process, syst)
  
 def GetHistoName(self):
  if self.histoName != '': return self.histoName
  hname = var + ('_' + self.chan if self.chan != '' else '') + ('_' + self.level if self.level != '' else '')
  self.SetHistoName(hname)
  return hname

 def ReadHistos(self):
   for k in self.dpr.keys():
     self.LoadHisto(self.dpr[k], k, '')
     for s in self.syst:
       self.LoadHisto(self.dpr[k], k, s)
   self.LoadHisto(self.dataFiles,'data_obs','')

 def Write(self):
  fname = self.GetOutFileName()
  if not os.path.isdir(self.outdir): os.mkdir(self.outdir)
  if os.path.isfile(fname): os.rename(fname, fname+'.bak')
  f = TFile(fname, 'recreate')
  print ' >> Saving histograms in: ' + fname
  for h in self.histos: h.Write()
  f.Close()

 def __init__(self, path, hname = '', outpath = './temp/', outname = '', rebin = 1):
  self.t = TopHistoReader(path)
  self.SetPath(path)
  self.SetRebin(rebin)
  self.SetHistoName(hname)
  self.SetOutputDir(outpath)
  self.SetOutName(outname)
  self.histos = []
  self.syst = []
  self.dpr = {}
  self.AddData()


