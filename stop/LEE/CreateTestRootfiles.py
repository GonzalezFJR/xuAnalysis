import os, sys
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)
from plotter.TopHistoReader import TopHistoReader, HistoManager
from plotter.Plotter import Stack, HistoComp
from framework.looper import looper
from ROOT.TMath import Sqrt as sqrt
from ROOT import kRed, kOrange, kBlue, kTeal, kGreen, kGray, kAzure, kPink, kCyan, kBlack, kSpring, kViolet, kYellow
from ROOT import TCanvas, gROOT, TLegend, TCanvas, TFile
gROOT.SetBatch(1)
from stop.config import *

GetPath    = lambda year, ms, ml : '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/29apr/LEE/Unc/SR/%s/mass%s_%s/tempfiles/'%(str(year), str(ms), str(ml))
#GetPath    = lambda year, ms, ml : '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/16apr/LEE_28apr/Unc/SR/%s/mass%s_%s/tempfiles/'%(str(year), str(ms), str(ml))
#GetPathNom = lambda year, ms, ml : '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/stop_v629Mar/Unc/SR/%s/mass%s_%s/tempfiles/'%(str(year), str(ms), str(ml))
GetHisto = lambda itoy : 'dnn_toy%s'%str(itoy) if itoy >=0 else 'dnn'
processes = ['Nonprompt', 'Others','tW','ttZ','tt_test']
nToys = 100

year = 2018
outpath = 'histos/'
outname = 'LEEpseudodata%s.root'%str(year)

def GetHistoFromFile(pr='tW', ms=275, ml=100, itoy=0, year=2018):
  f = TFile.Open( (GetPath(year, ms, ml)) +pr+'.root')# if itoy>=0 else GetPathNom(year, ms, ml) ) +pr+'.root')
  h = f.Get(GetHisto(itoy))
  h.SetDirectory(0)
  h.Scale(1000*GetLumi(year))
  f.Close()
  return h

def GetPseudoDataHisto(ms=275, ml=100, itoy=0, year=2018):
  h = GetHistoFromFile(processes[0], ms, ml, itoy, year)
  for pr in processes[1:]:
    h.Add(GetHistoFromFile(pr, ms, ml, itoy, year))
  h.SetDirectory(0)
  name = ('pseudodata_%s_%s_toy%s'%(str(ms), str(ml), str(itoy))) if itoy >= 0 else 'pseudodata_%s_%s'%(str(ms), str(ml))
  h.SetName(name); h.SetTitle(name)
  return h

if not outpath.endswith('/'): outpath+='/'
if not os.path.isdir(outpath): os.system('mkdir -p %s'%outpath)
f = TFile.Open(outpath+outname, 'recreate' )
stopmasses = GetAllStopNeutralinoPoints(mode='diag')
for ms, ml in stopmasses:
  for itoy in range(-1,nToys):
    h = GetPseudoDataHisto(ms, ml, itoy, year)
    f.cd()
    h.Write()
f.Close()
