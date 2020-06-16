'''
 python CreateRootFiles.py -s tt -n 100 --sendJobs --mStop 275 --mLSP 100 #-q short
'''
nSlots = 8
massSelect = 'diag'

import os, sys
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)
from stop.config import *
from plotter.TopHistoReader import TopHistoReader, HistoManager
from plotter.Plotter import Stack, HistoComp
from framework.looper import looper
from ROOT.TMath import Sqrt as sqrt
from ROOT import kRed, kOrange, kBlue, kTeal, kGreen, kGray, kAzure, kPink, kCyan, kBlack, kSpring, kViolet, kYellow
from ROOT import TCanvas, gROOT, TLegend, TCanvas, TFile
from numpy import arange
gROOT.SetBatch(1)
import argparse

parser = argparse.ArgumentParser(description='To select masses and year')
parser.add_argument('--year',         default=2018   , help = 'Year')
parser.add_argument('--mStop',        default=275  , help = 'Stop mass')
parser.add_argument('--mLSP',         default=100  , help = 'Neutralino mass')
parser.add_argument('--mStopIn',        default=275  , help = 'Stop mass')
parser.add_argument('--mLSPIn',         default=100  , help = 'Neutralino mass')
parser.add_argument('--region',       default='SR'  , help = 'Select the region')
parser.add_argument('--channel','-c', default='emu'  , help = 'Select the channel')

#args = parser.parse_args()
args, unknown = parser.parse_known_args()

ms   = int(args.mStop)
ml   = int(args.mLSP)

msin = int(args.mStopIn)
mlin = int(args.mLSPIn)
year = int(args.year)
chan = args.channel
argprocess = ''
treeName="MiniTree"
nSlots = 1

region = 'SR'


GetPath = lambda chan, year, ms, ml: baseoutpath+'/Unc/%s/%s/%i/mass%i_%i/tempfiles/'%(region, chan, year, ms, ml)
outpath = lambda chan,year,ms,ml : '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/stop/LEE/injected%i_%i/%s/%i/mass%i_%i/'%(msin, mlin, chan, year, ms, ml)
bkg = ['tt_test', 'Nonprompt', 'Others', 'tW', 'ttZ', 'ttnongauss', 'tt_UEUp', 'tt_hdampUp', 'tt_hdampDown', 'tt_UEDown', 'tt_mtopDown', 'tt_mtopUp', 'data']
out = {}

def AddHistosFromFile(path, sampleName):
  if ' ' in sampleName: sampleName = sampleName.replace(' ', '')
  if not sampleName in out.keys(): out[sampleName] = {}
  print 'Reading %s from %s...'%(sampleName, path)
  f = TFile.Open('%s/%s.root'%(path, sampleName))
  hlist = f.GetListOfKeys()
  for l in hlist:
    hname = l.GetName()
    histo = getattr(f, hname)
    histo.SetDirectory(0)
    out[sampleName][hname] = histo

def Save(chan, year=None, ms=None, ml=None, var='dnn'):
  if isinstance(chan, list):
    if   len(chan) == 4: chan, year, ms, ml = chan
    elif len(chan) == 5: chan, year, ms, ml, var = chan
  for b in bkg: AddHistosFromFile(GetPath(chan,year, ms, ml), b) 
  AddHistosFromFile(GetPath(chan, year, msin, mlin), 'stop_test')

  processes = bkg + ['stop_test']
  processes.pop(processes.index('data'))
  hm = HistoManager(processes, path = '', processDic = processDic[year], lumi = GetLumi(year)*1000.,indic = out)
  hm.SetHisto(var)
  os.system("mkdir -p %s"%outpath(chan,year,ms,ml))
  hm.Save(outname = outpath(chan,year,ms,ml)+'/'+var, htag='')

if nSlots == 1:
  print 'Running secuencial...'
  for ms,ml in GetAllStopNeutralinoPoints(mode=massSelect): Save(chan, year, ms, ml)
else:
  print 'Running with %i slots!!'%nSlots
  from multiprocessing import Pool
  pool = Pool(nSlots)
  listOfImputs = []
  for ms,ml in GetAllStopNeutralinoPoints(mode=massSelect): listOfImputs.append([chan, year, ms, ml])
  results = pool.map(Save, listOfImputs)
  pool.close()
  pool.join()
