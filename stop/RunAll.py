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
esentialstopmasses = [[235,60]]#[[225, 50], [275, 100]]#, [245,100], [275, 70]] # [245, 70]


samplesSlots = {
          'tt_test'     : 10,
          'stop_test'   : 5,
          'ttnongauss'  : 20,
          'tt'          : 20,
          'stop'        : 5,
          'tW'          : 5,
          'ttZ'         : 10,
          'Nonprompt'   : 5,
          'Others'      : 3,
          'tt_hdampUp'  : 3,
          'tt_UEUp'     : 3,
          'tt_hdampDown': 3,
          'tt_UEDown'   : 3,
          'tt_mtopDown' : 3, 
          'tt_mtopUp'   : 3, 
          'data'        : 2, 
}


import time
start = time.time()
def PrintProgress(count, total):
  sec = time.time()-start
  speed = count/sec
  cremain = total-count
  tremain = cremain/speed
  print '[%i / %i] --- %1.2f s, [exp %i s]'%(count, total, sec, tremain)
  return count+1

nparal = 10

stopmasses = GetAllStopNeutralinoPoints(mode='')
years = [2016, 2017, 2018]
channels = ['ee','emu','mumu']
total = len(stopmasses)*len(years)*len(channels)
count = 0
nslots = 2
listInputs = []
for year in years:
  for sm, nm in stopmasses:#esentialstopmasses:#stopmasses:
    for ch in channels:
      listInputs.append([ch, year, sm, nm])
      #for samp in samplesSlots:

def Run(inputs):
  ch, year, sm, nm = inputs
  name = "year %i, stop%i_%i"%(year, sm, nm)
  #os.system('python CreateRootFiles.py --year %i --mStop %i --mLSP %i --SR -n %i -c %s -s DY --sendJobs -q cpupower'%(year, sm, nm, nslots, ch))
  #if year == 2016: os.system('python RunFSR2016.py --year %i --mStop %i --mLSP %i --SR -n 3 -c %s'%(year, sm, nm, ch))
  os.system('python CreateRootFiles.py --year %i --mStop %i --mLSP %i --SR -n %i -c %s'%(year, sm, nm, nslots, ch))
  #os.system('python CalculatePDFweights.py --year %i --mStop %i --mLSP %i --SR -c %s'%(year, sm, nm, ch))
  os.system('python CraftUncertainties.py --year %i --mStop %i --mLSP %i -c %s'%(year, sm, nm, ch))


from multiprocessing import Pool
pool = Pool(nparal)
results = pool.map(Run, listInputs)
pool.close()
pool.join()
















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

