import os, sys
from plotterconf import *
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)
from ROOT.TMath import Sqrt as sqrt
from ROOT import kRed, kOrange, kBlue, kTeal, kGreen, kGray, kAzure, kPink, kCyan, kBlack, kSpring, kViolet, kYellow
from ROOT import TCanvas, gROOT
gROOT.SetBatch(1)

processDic = {
'VV'  : 'WZTo3LNU,WWTo2L2Nu,ZZTo2L2Nu,ZZTo4L',
'Nonprompt': 'W0JetsToLNu,W1JetsToLNu,W2JetsToLNu,W3JetsToLNu',#'TTsemilep',
'tW'  : 'tW_noFullHad,  tbarW_noFullHad',
#'DY'  : 'DYJetsToLL_MLL50',
'DY'  : 'DYJetsToLL_M_10to50,DYJetsToLL_MLL50',
'tt'  : 'TT',
'tt_hdampDown' : 'TT_hdampDOWN',
'tt_hdampUp' :  'TT_hdampUP',
'tt_UEDown' : 'TT_TuneCP5down',
'tt_UEUp' : 'TT_TuneCP5up',
'data': 'HighEGJet, SingleMuon'}##SingleMuon

doBlind = False
processes = ['VV', 'Nonprompt', 'DY', 'tt', 'tW']
hm = HistoManager(processes, systematics, '', path=path, processDic=processDic, lumi = Lumi)

def Draw(var = 'H_Lep0Pt_ElMu_2jets', ch = '', lev = 'dilepton', rebin = 1, xtit = '', ytit = 'Events', doStackOverflow = False, binlabels = '', setLogY = False, maxscale = 1.6, rangeX=[0,0]):
  s = Stack(outpath=outpath)
  s.SetRangeX(rangeX)
  s.SetColors(colors)
  s.SetProcesses(processes)
  s.SetLumi(Lumi)
  s.SetHistoPadMargins(top = 0.08, bottom = 0.10, right = 0.06, left = 0.10)
  s.SetRatioPadMargins(top = 0.03, bottom = 0.40, right = 0.06, left = 0.10)
  s.SetTextLumi(texlumi = '%2.1f pb^{-1} (5.02 TeV)', texlumiX = 0.62, texlumiY = 0.97, texlumiS = 0.05)
  s.SetBinLabels(binlabels)
  hm.SetStackOverflow(doStackOverflow)
  hm.IsScaled = False
  name = GetName(var, ch, lev)
  if ch == 'all': name = [GetName(var,x,lev) for x in ['ElMu','ElEl','MuMu']]#GetName(var,'ElMu',lev)+','+GetName(var,'ElEl',lev)+','+GetName(var,'MuMu',lev)
  hm.SetHisto(name, rebin)
  if doBlind: hm.indic['data'][var] = hm.GetSumBkg()
  #for pr in processes: print '%s : %1.2f'%(pr, hm.indic[pr][name].Integral())
  s.SetHistosFromMH(hm)
  # Blind
  if doBlind:
    hData  = s.TotMC.Clone("Asimov")
    hData.SetLineWidth(0); hData.SetMarkerStyle(20); hData.SetMarkerColor(kGray)
    hData2 = hData.Clone("Asimov2")
    hData2.Divide(hData)
    s.SetDataHisto(hData)
    s.SetRatio(hData2)
  s.SetTextChan('')
  s.SetRatioMin(2-maxscale)
  s.SetRatioMax(maxscale)
  if ch == 'MuMu': tch = '#mu#mu'
  elif ch == 'ElEl': tch = 'ee'
  else: tch = 'e#mu'
  if   lev == '2jets': Tch = tch+', #geq 2 jets'
  elif lev == '1btag': Tch =tch+ ', #geq 2 jets, #geq 1 btag'
  else: Tch=tch
  s.SetTextChan(Tch)
  tch=''
  s.SetLogY(setLogY)
  s.SetPlotMaxScale(maxscale)
  s.SetOutName(GetName(var,ch,lev)+('_log' if setLogY else ''))
  s.DrawStack(xtit, ytit)

#Draw('NJets', 'ElMu', '2jets', 2, 'Lep #eta', 'Events', False, maxscale = 1.9)
for ch in ['ElMu','MuMu','ElEl']:
  Draw('BDT1j1b', ch, 'dilepton', 5, 'BDT output 1j1b', 'Events', True, maxscale = 1.6, rangeX=[])#rangeX=[-0.7, -0.2])
  #Draw('BDT2j1b', ch, 'dilepton', 5, 'BDT output 2j1b', 'Events', True, maxscale = 1.6, rangeX=[])#rangeX=[-0.6, 0.5])
  #Draw('NBtagNJets_3bins', ch, 'dilepton', 1, '(nJets, nBtags)', 'Events', True, binlabels = ['(1,1)', '(2,1)', '(2,2)'])

