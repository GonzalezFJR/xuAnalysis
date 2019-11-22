import os, sys
#from confww import *
from plotterconf import *
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)
from ROOT.TMath import Sqrt as sqrt
from ROOT import kRed, kOrange, kBlue, kTeal, kGreen, kGray, kAzure, kPink, kCyan, kBlack, kSpring, kViolet, kYellow
from ROOT import TCanvas, gROOT
gROOT.SetBatch(1)

hm = HistoManager(processes, systematics, '', path=path, processDic=processDic, lumi = Lumi)

def Draw(var = 'H_Lep0Pt_ElMu_2jets', ch = '', lev = 'dilepton', rebin = 1, xtit = '', ytit = 'Events', doStackOverflow = False, binlabels = '', setLogY = False, maxscale = 1.6):
  s = Stack(outpath=outpath+'/WW/')
  s.SetColors(colors)
  s.SetProcesses(processes)
  s.SetLumi(Lumi)
  s.SetHistoPadMargins(top = 0.08, bottom = 0.10, right = 0.06, left = 0.10)
  s.SetRatioPadMargins(top = 0.03, bottom = 0.40, right = 0.06, left = 0.10)
  s.SetTextLumi(texlumi = '%2.1f pb^{-1} (5.02 TeV)', texlumiX = 0.62, texlumiY = 0.97, texlumiS = 0.05)
  s.SetBinLabels(binlabels)
  hm.SetStackOverflow(doStackOverflow)
  name = GetName(var, ch, lev)
  hm.IsScaled = False
  hm.SetHisto(name, rebin)
  s.SetHistosFromMH(hm)
  s.SetOutName(name)
  s.SetTextChan('')
  s.SetRatioMin(2-maxscale)
  s.SetRatioMax(maxscale)
  if ch == 'MuMu': tch = '#mu#mu'
  elif ch == 'ElEl': tch = 'ee'
  else: tch = 'e#mu'
  Tch=tch + ', 0 jets, p_{T}^{%s} > 30 GeV'%tch
  s.SetTextChan(Tch)
  tch=''
  s.SetLogY(setLogY)
  s.SetPlotMaxScale(maxscale)
  s.DrawStack(xtit, ytit)


lev = 'ww'
chan = 'ElMu'

Draw('NJets',  chan, lev, 1, 'Jet multiplicity', 'Events', True)
Draw('Lep0Pt', chan, lev, 2, 'Leading lep p_{T} (GeV)', 'Events', True, maxscale = 1.6)
Draw('Lep1Pt', chan, lev, 2, 'Subeading lep p_{T} (GeV)', 'Events', False, maxscale = 1.6)
Draw('DilepPt', chan, lev, 2, 'Dilepton p_{T} (GeV)', 'Events', False, maxscale = 1.6)
Draw('DeltaPhi', chan, lev, 2, '#Delta#phi(ll) (GeV)', 'Events', False, maxscale = 1.6)
Draw('MET', chan, lev, 2, 'MET (GeV)', 'Events', False, maxscale = 1.6)
Draw('InvMass', chan, lev, 6, 'm_{e#mu} (GeV)', 'Events', False, maxscale = 1.6 )

