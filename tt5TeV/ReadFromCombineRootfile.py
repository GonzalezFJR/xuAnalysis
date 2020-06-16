import os, sys
from plotterconf import outpath,colors, Lumi, folder
from plotter.TopHistoReader import TopHistoReader, HistoManager
from plotter.Plotter import Stack, HistoComp, HistoUnc
from framework.looper import looper
from ROOT.TMath import Sqrt as sqrt
from ROOT import kRed, kOrange, kBlue, kTeal, kGreen, kGray, kAzure, kPink, kCyan, kBlack, kSpring, kViolet, kYellow
from ROOT import TCanvas, gROOT, TLegend, TCanvas
gROOT.SetBatch(1)

syst = "MuonEff, ElecEff, TrigEff, Prefire, JES, JER, Prefire, PU, PDF, Scale, ISR, FSR, hdamp, UE"
processes  = 'VV, Nonprompt, DY, tW, tt'.replace(' ', '').split(',')
path = '/nfs/fanae/user/juanr/CMSSW_10_2_13/src/tt5TeV/histos/'+folder
normunc={'tt':0.06, 'Nonprompt':0.5, 'DY':0.3,'VV':0.3,'tW':0.20}

pltlabel = {
  'ElMu' : {
    'dilepton' : 'e#mu',
    '2jets' : 'e#mu, #geq 2 jets',
  },
  'ElEl' : {
    'dilepton' : 'ee',
    '2jetsnomet' : 'ee, Z veto, #geq 2 jets',
    '2jets' : 'ee, Z Veto, p_{T}^{miss}#geq 30 GeV, #geq 2 jets',
  },
  'MuMu' : {
    'dilepton' : '#mu#mu',
    '2jetsnomet' : '#mu#mu, Z veto, #geq 2 jets',
    '2jets' : '#mu#mu, Z veto, p_{T}^{miss}#geq 30 GeV, #geq 2 jets',
  },
}

titdic = {
  'Lep0Eta' : 'Leading lepton #eta',
  'Lep1Eta' : 'Subleading lepton #eta',
  'MuonEta' : '#eta^{#mu}',
  'ElecEta' : '#eta^{e}',
  'Lep0Pt'  : 'Leading lepton p_{T} (GeV)',
  'Lep1Pt'  : 'Subleading lepton p_{T} (GeV)',
  'MuonPt'  : 'p_{T}^{#mu} (GeV)',
  'ElecPt'  : 'p_{T}^{e} (GeV)',
  'MET'     : 'p_{T}^{miss} (GeV)',
  'DYMass'  : 'm(%s) (GeV)',
  'InvMass' : 'm(%s) (GeV)',
  'NJets'   : 'Jet multiplicity',
  'HT'      : 'H_{T} (GeV)',
  'DilepPt' : 'p_{T}(%s) (GeV)',
  'Jet0Pt'  : 'Leading jet p_{T} (GeV)',
  'Jet1Pt'  : 'Subleading jet p_{T} (GeV)',
  'Jet0Eta' : 'Leading jet #eta',
  'Jet1Eta' : 'Subleading jet #eta',
  'DeltaPhi': '#Delta#phi(%s) (rad/#pi)',
  #'NBtags'  : 'b-tag multiplicity',
}

rebin={
  'DYMass' : 2,
  'DilepPt': 5,
  'HT' : 10,
  'InvMass' : 10,
  'Jet0Eta' : 10,
  'Jet1Eta' : 10,
  'DeltaPhi': 4,
  'Lep0Eta' : 5,
  'Lep1Eta' : 5,
  'MET' : 3,
  'Lep0Pt':4,
}

ran={
  'NJets' : {'dilepton' : [0,5], '2jets':[2,6]},
  'HT' : {'dilepton':[25,300],'2jets':[50,400]},
}

def StackPlot(var='NJets', ch='ElMu', lev='2jets', blind=False, ratiolims=[0.4, 1.6], binlabels='', rangeX=[0,0]):
  hm = HistoManager(processes, syst, path=path)
  fname = '%s%s%s'%(var, ('_'+ch) if ch!='' else '', ('_'+lev) if lev!='' else '')
  hm.ReadHistosFromFile(fname, rebin=(rebin[var] if var in rebin.keys() else 1))
  hm.AddNormUnc(normunc) 
  hm.GetDataHisto()
  s = Stack(outpath=outpath+'/stackplots/')
  s.SetRangeX(rangeX)
  s.SetColors(colors)
  s.SetProcesses(processes)
  s.SetLumi(Lumi)
  s.SetRangeX(ran[var][lev] if var in ran and (isinstance(ran[var], dict) and lev in ran[var].keys()) else (ran[var] if var in ran.keys() else [0,0]))
  s.SetHistoPadMargins(top = 0.08, bottom = 0.10, right = 0.06, left = 0.10)
  s.SetRatioPadMargins(top = 0.03, bottom = 0.40, right = 0.06, left = 0.10)
  s.SetTextLumi(texlumi = '%2.1f pb^{-1} (5.02 TeV)', texlumiX = 0.62, texlumiY = 0.97, texlumiS = 0.05)
  if binlabels!='': s.SetBinLabels(binlabels)
  s.SetOutName('stack_'+fname)
  s.SetHistosFromMH(hm)
  s.SetTextChan(pltlabel[ch][lev] if (ch in pltlabel and lev in pltlabel[ch]) else '', x=0.18, s=0.036)
  xtit = titdic[var] if var in titdic else ''
  if ('%s') in xtit: xtit = xtit%pltlabel[ch]['dilepton']
  rmin, rmax = ratiolims
  s.SetRatioMin(rmin); s.SetRatioMax(rmax)
  s.SetYratioTitle('Data/Pred.')
  s.SetPlotMaxScale(1.8)
  # blind
  if blind:
    hData  = s.TotMC.Clone("Asimov")
    hData.SetLineWidth(0); hData.SetMarkerStyle(20); hData.SetMarkerColor(kGray)
    hData2 = hData.Clone("Asimov2")
    hData2.Divide(hData)
    s.SetDataHisto(hData)
    s.SetRatio(hData2)

  s.DrawStack(xtit, 'Events')
  if var == 'NJets' and lev == 'dilepton':
    s.SetLogY()
    s.SetPlotMaxScale(100)
    s.SetPlotMinimum(0.5)
    s.SetOutName('stack_log_'+fname)
    s.DrawStack(xtit, 'Events')

StackPlot('ttxsec_allchan', '', '',blind=False, ratiolims=[0.8, 1.4], binlabels=['ee', 'e#mu', '#mu#mu'])
#StackPlot('NJets', 'ElMu', 'dilepton',blind=False, ratiolims=[0.2, 1.8], rangeX=[0,5])


for var in ['Jet0Eta', 'Jet1Eta', 'DeltaPhi']:#titdic.keys():
  for ch in ['ElMu', 'ElEl', 'MuMu']:
    for lev in ['dilepton', '2jets', '2jetsnomet']:
      fname = '%s_%s_%s'%(var,ch,lev)
      if not os.path.isfile(path+fname+'.root'): continue
      binlabel = ''
      StackPlot(var, ch, lev, blind=False)
