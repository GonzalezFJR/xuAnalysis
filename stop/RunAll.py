import os, sys
from config import *
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)
from plotter.TopHistoReader import TopHistoReader, HistoManager
from plotter.Plotter import Stack, HistoComp
from framework.looper import looper
from ROOT.TMath import Sqrt as sqrt
from ROOT import kRed, kOrange, kBlue, kTeal, kGreen, kGray, kAzure, kPink, kCyan, kBlack, kSpring, kViolet, kYellow
from ROOT import TCanvas, gROOT, TLegend, TCanvas
from numpy import arange

gROOT.SetBatch(1)

stopmasses = GetAllStopNeutralinoPoints()
for year in [2016, 2017, 2018]:#, 2017, 2018]:
  for sm, nm in stopmasses:
    name = "year %i, stop%i_%i"%(year, sm, nm)
    #print name

    os.system('python CreateRootFiles.py --year %i --mStop %i --mLSP %i --SR -n 10'%(year, sm, nm))
    os.system('python RunFSR2016.py --year %i --mStop %i --mLSP %i --SR -n 2'%(year, sm, nm))
    os.system('python CalculatePDFweights.py --year %i --mStop %i --mLSP %i --SR -n 5'%(year, sm, nm))

    #os.system('python CalculatePDFweights.py --year %i --mStop %i --mLSP %i --SR'%(year, sm, nm))
    #os.system('python CraftUncertainties.py --year %i --mStop %i --mLSP %i'%(year, sm, nm))

exit()
path  = '../stop_v611Feb/Unc/%s/%i/mass%s/tempfiles/'
path2 = '../stop_v6NewSyst/Unc/%s/%i/mass%s/tempfiles/'
year = 2017
region = 'SR'

stopmasses = GetAllStopNeutralinoPoints()
for sm, nm in stopmasses:
  name = "%i_%i"%(sm, nm)
  p = path%(region, year, name)
  p2 = path2%(region, year, name)
  os.system('python %s/framework/merger.py %s -frv'%(basepath, p))
  os.system('mv %s/tt_hdamp*.root %s/'%(p, p2))

