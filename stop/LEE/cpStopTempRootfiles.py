import os, sys
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)
from stop.config import *
from plotter.TopHistoReader import TopHistoReader, HistoManager
from plotter.Plotter import Stack, HistoComp
from framework.looper import looper
from ROOT.TMath import Sqrt as sqrt
from ROOT import kRed, kOrange, kBlue, kTeal, kGreen, kGray, kAzure, kPink, kCyan, kBlack, kSpring, kViolet, kYellow
from ROOT import TCanvas, gROOT, TLegend, TCanvas
from numpy import arange

gROOT.SetBatch(1)
esentialstopmasses = [[225, 50], [275, 100]]#, [245,100], [275, 70]] # [245, 70]

opath  = lambda ms, ml, year : '../../29apr/LEE/Unc/SR/%s/mass%s_%s/tempfiles/'%(str(year), str(ms), str(ml))
inpath = lambda ms, ml, year : '../../29apr/Unc/SR/emu/%s/mass%s_%s/tempfiles/'%(str(year), str(ms), str(ml))
fnames = ['stop_test', 'data']

stopmasses = GetAllStopNeutralinoPoints()
for year in [2018]:#, 2017, 2018]:
  for sm, nm in stopmasses:
    for f in fnames:
      os.system('cp %s/%s.root %s'%(inpath(sm, nm, year), f, opath(sm, nm, year) ))
