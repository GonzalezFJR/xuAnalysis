import os,sys
sys.path.append(os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/')
from plotter.TopHistoReader import TopHistoReader
from plotter.WeightReader import WeightReader
from ROOT.TMath import Sqrt as sqrt
from scripts.DrellYanDataDriven import DYDD
from scripts.NonpromptDataDriven import NonpromptDD
from plotterconf import *

### Input and output
DYsamples   = processDic['DY']
datasamples = processDic['data']

def DrawDYDD(lev = '2jets', doSF = False):
  if not doSF and lev == 'MET': return 
  d = DYDD(path,outpath,'ElMu',lev, DYsamples=DYsamples, DataSamples=datasamples, lumi=Lumi, histonameprefix='')  #, hname = 'DYHistoElMu' if not doSF else 'DYHisto')
  d.SetHistoNameOF('DYHistoElMu')
  d.SetHistoNameSF('DYHisto')
  lab = 'SF' if doSF else 'OF'
  d.PrintDYestimate(doSF,  'DYDD_'+lev+'_'+lab)

def DrawDYDDnjets(lev='2jets'):
  d = DYDD(path,outpath,lev)
  d.PrintDYSFnjets()

def DrawNonprompt(lev = '2jets', ch = 'ElMu'):
  d = NonpromptDD(path,outpath,ch,lev, process=processDic , lumi=Lumi, histonameprefix='',yieldsSSname='YieldsSS')
  d.PrintSSyields('SSyields_'+lev, lev)
  for chan in ['ElEl', 'MuMu', 'ElMu']:
    d.PrintNonpromptEstimate('NonpromptDD_'+lev+'_'+chan, chan, lev)

# DY
#for ilev in ['dilepton','2jets']:
DrawDYDD('2jets')
DrawDYDD('2jets',True)

# Nonprompt 
#for ilev in ['2jets']: #['dilepton','MET','1btag','2jets', 'ZVeto']:
#  DrawNonprompt(ilev)

