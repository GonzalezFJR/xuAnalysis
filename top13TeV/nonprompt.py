import os,sys
sys.path.append(os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/')
from plotter.TopHistoReader import TopHistoReader
from plotter.WeightReader import WeightReader
from ROOT.TMath import Sqrt as sqrt
from tt13TeV.NonpromptDataDriven import NonpromptDD
from conf_andrea import *

### Input and output
year = 2018
path = path[year]

outpath = './outputs/'

def DrawNonrpompt(lev = '2jets'):
  d = NonpromptDD(path,outpath,'ElMu',lev, process=processDic[year] , lumi = GetLumi(year)*1000) 
  d.PrintSSyields('SSyields_'+lev, lev)
  for chan in ['Elec', 'Muon', 'ElMu']:
    d.PrintNonpromptEstimate('NonpromptDD_'+lev+'_'+chan, chan, lev)

DrawNonrpompt()

