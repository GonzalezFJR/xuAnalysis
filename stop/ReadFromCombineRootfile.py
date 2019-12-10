import os, sys
from config import *
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)
from plotter.TopHistoReader import TopHistoReader, HistoManager
from plotter.Plotter import Stack, HistoComp, HistoUnc
from framework.looper import looper
from ROOT.TMath import Sqrt as sqrt
from ROOT import kRed, kOrange, kBlue, kTeal, kGreen, kGray, kAzure, kPink, kCyan, kBlack, kSpring, kViolet, kYellow
from ROOT import TCanvas, gROOT, TLegend, TCanvas

gROOT.SetBatch(1)
syst = 'MuonEff, ElecEff, Trig, Pref, JES, JER, MuonES, Uncl, Btag, MisTag, TopPt, hdamp, UE, PU'
process = 'tt'#, tW, ttZ, Others'
path = 'Unc/SR/'
outpath = '/nfs/fanae/user/juanr/www/stopLegacy/unc/'
year = 2018


#for pr in process.replace(' ', '').split(','):
#  print '%s : %1.2f'%(pr, hm.GetCYield(pr))
#print 'y = ', hm.GetCYield('tt', syst)
#for s in syst.replace(' ', '').split(','):
#  n = hm.GetCYield('tt')
#  v = hm.GetCYield('tt', s)
#  print '%s : %1.2f'%(s, abs(n-v)/n*100)

#print 'y = ', hm.GetCYield('tt')

syst = 'MuonEff, ElecEff, Trig, Pref, JES, JER, MuonES, Uncl, Btag, MisTag, UE, hdamp'
sysdic = {
'MuonEff' : 'Muon efficiency',
'ElecEff' : 'Electron efficiency',
'Trig'    : 'Trigger efficiency',
'Pref'    : 'Prefire correction',
'JES'     : 'Jet energy scale',
'JER'     : 'Jet energy resolution',
'MuonES'  : 'Muon energy scale',
'Uncl'    : 'Unclustered energy',
'Btag'    : 'b-tag efficiency',
'MisTag'  : 'MisTag efficiency',
#'TopPt'   : 'Top quark p_{T}',
#'hdamp'   : 'h_{damp} variations',
#'UE'      : 'UE Tune',
'PU'      : 'Pileup reweighting',
}

titdic = {
  'mt2' : 'm_{T2} (GeV)',
  'met' : 'MET (GeV)',
  'dnn' : 'DNN score',
}

def SavePlots(syst, var = 'mt2', sampName = 'tt'):
  hm = HistoManager(process, syst, path=path)
  hm.ReadHistosFromFile(var)
  hm.GetDataHisto()
  a = HistoUnc(outpath, var+sampName+s, tag=sysdic[s], xtit = titdic[var] if var in titdic.keys() else '')
  a.SetLumi(GetLumi(year))
  a.AddHistoNom(hm.GetHisto(sampName, sampName))
  a.AddHistoUp(hm.GetHisto(sampName, sampName, s+'Up'))
  a.AddHistoDown(hm.GetHisto(sampName, sampName, s+'Down'))
  a.Draw()

def StackPlot(var = 'mt2', xtit = 'm_{T2} (GeV)'):
  hm = HistoManager(process, syst, path=path)
  hm.ReadHistosFromFile(var)
  hm.GetDataHisto()
  s = Stack(outpath=outpath)
  s.SetColors(colors)
  s.SetProcesses(processes)
  s.SetLumi(GetLumi(year))
  s.SetOutName('stack_'+var)
  s.SetHistosFromMH(hm)
  s.DrawStack(xtit, 'Events')

for var in ['met', 'mt2', 'dnn']:
  #StackPlot(var)
  for s in sysdic.keys(): 
    if s == 'Pref' and year == 2018: continue
    SavePlots(s,var)

