import os, sys
from plotterconf import *
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)
from ROOT.TMath import Sqrt as sqrt
from ROOT import kRed, kOrange, kBlue, kTeal, kGreen, kGray, kAzure, kPink, kCyan, kBlack, kSpring, kViolet, kYellow
from ROOT import TCanvas, gROOT
gROOT.SetBatch(1)

######################################################################################
### Plots

hm = HistoManager(processes, systematics, '', path=path, processDic=processDic, lumi = Lumi)

def Draw(name = 'Lep0Pt_eee_lep', rebin = 1, xtit = '', ytit = 'Events', doStackOverflow = False, binlabels = '', setLogY = False, maxscale = 2):
  s = Stack(outpath=outpath, doRatio = False)
  s.SetColors(colors)
  s.SetProcesses(processes)
  s.SetLumi(Lumi)
  s.SetHistoPadMargins(top = 0.08, bottom = 0.10, right = 0.06, left = 0.10)
  s.SetRatioPadMargins(top = 0.03, bottom = 0.40, right = 0.06, left = 0.10)
  s.SetTextLumi(texlumi = '%2.1f pb^{-1} (5.02 TeV)', texlumiX = 0.61, texlumiY = 0.96, texlumiS = 0.05)
  s.SetTextCMSmode(y = 0.865, s = 0.052)
  s.SetTextCMS(y = 0.87, s = 0.06)
  hm.SetStackOverflow(doStackOverflow)
  hm.SetHisto(name, rebin)
  s.SetHistosFromMH(hm)
  s.SetOutName(name)
  s.SetBinLabels(binlabels)
  s.SetTextChan('')
  s.SetRatioMin(2-maxscale)
  s.SetRatioMax(maxscale)
  s.SetTextChan('')
  s.SetLogY(setLogY)
  s.SetPlotMaxScale(maxscale)
  s.SetXtitle(size = 0.05, offset = 0.8, nDiv = 510, labSize = 0.04)
  s.SetYtitle(labSize = 0.04)
  s.DrawStack(xtit, ytit)

#lev = 'met' #lep, met
for lev in ['met', 'lep']:
 Draw(GetAllCh('m3l', lev), 10, 'm_{3l} (GeV)',      'Events / 10 GeV')
 Draw(GetAllCh('mtw', lev), 6, 'm_{T}^{W} (GeV)',    'Events')
 Draw(GetAllCh('mz', lev), 10, 'm_{Z} (GeV)',        'Events / 10 GeV')
 Draw(GetAllCh('MET', lev), 2, 'p_{T}^{miss} (GeV)', 'Events / 10 GeV')

'''
Draw(GetAllCh('LepWPt', lev), 4, 'p_{T}(lepW)  (GeV)', 'Events / 40 GeV')
Draw(GetAllCh('LepWEta', lev), 10, '#eta (lepW)', 'Events')
Draw(GetAllCh('LepWPhi', lev), 5, '#phi (lepW) (rad/#pi)', 'Events')
Draw(GetAllCh('LepZ0Pt', lev), 4, 'p_{T}(lep0Z)  (GeV)', 'Events / 40 GeV')
Draw(GetAllCh('LepZ0Eta', lev), 10, '#eta (lep0Z)', 'Events')
Draw(GetAllCh('LepZ0Phi', lev), 5, '#phi (lep0Z) (rad/#pi)', 'Events')
Draw(GetAllCh('LepZ1Pt', lev), 4, 'p_{T}(lep1Z)  (GeV)', 'Events / 40 GeV')
Draw(GetAllCh('LepZ1Eta', lev), 10, '#eta (lep1Z)', 'Events')
Draw(GetAllCh('LepZ1Phi', lev), 5, '#phi (lep1Z) (rad/#pi)', 'Events')
Draw(GetAllCh('TrilepPt', lev), 8, 'Trilep p_{T} (GeV)', 'Events')
Draw(GetAllCh('ZPt', lev),  8, 'Z p_{T} (GeV)', 'Events')
Draw(GetAllCh('MaxDeltaPhi', lev), 2, 'max(#Delta#phi (ll)) (rad/#pi)', 'Events')
Draw(GetAllCh('NJets', lev), 1, 'Jet multiplicity', 'Events', True)
'''
