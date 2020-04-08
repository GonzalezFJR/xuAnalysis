import os,sys
sys.path.append(os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/')
from plotter.TopHistoReader import TopHistoReader
from plotter.WeightReader import WeightReader
from ROOT.TMath import Sqrt as sqrt
from tt13TeV.DrellYanDataDriven import DYDD
from conf_andrea import *

### Input and output
year = 2018
path = path[year]
DYsamples   = processDic[year]['DY']
datasamples = processDic[year]['data']

outpath = './outputs/'

def DrawDYDD(lev = '2jets', doSF = False):
  if not doSF and lev == 'MET': return 
  d = DYDD(path,outpath,'ElMu',lev, DYsamples=DYsamples, DataSamples=datasamples, lumi = GetLumi(year)*1000) 
  lab = 'SF' if doSF else 'OF'
  d.PrintDYestimate(doSF,  'DYDD_'+lev+'_'+lab)

def DrawDYDDnjets():
  d = DYDD(path,outpath)
  d.PrintDYSFnjets()

DrawDYDD()
