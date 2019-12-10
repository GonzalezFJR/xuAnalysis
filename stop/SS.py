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
gROOT.SetBatch(1)

outpath = './SS/'

#Tm_LSP, Tm_stop
treeName="MiniTree"
year = 2018
ms = 275
ml = 100


vardic = {
  'mt2'      : 'm_{T2} (GeV)',
  'met'      : 'MET (GeV)',
  'mll'      : 'm_{e#mu} (GeV)',
  'dnn'      : 'DNN score',
  'dileppt'  : 'p_{T}^{e#mu} (GeV)',
  'deltaphi' : '#Delta#phi (rad/#pi)',
  'deltaeta' : '#Delta#eta',
  'ht'       : 'H_{T} (GeV)',
  'lep0pt'   : 'Leading lepton p_{T} (GeV)',
  'lep1pt'   : 'Subleading lepton p_{T} (GeV)',
  'lep0eta'  : 'Leading lepton #eta',
  'lep1eta'  : 'Subleading lepton #eta',
}

processDic = {
2018 : {
         'Charge flips' : 'TTTo2L2Nu, tbarW_noFullHad, tW_noFullHad',
         'Prompt SS' : 'TTTo2L2Nu, tbarW_noFullHad, tW_noFullHad, TTWJetsToLNu, TTWJetsToQQ, WZTo3LNu, ZZTo4L',
         'Semileptonic tt' : 'TTToSemiLeptonic',
         'Other nonprompt':'WJetsToLNu_MLM,TTTo2L2Nu, tbarW_noFullHad, tW_noFullHad, DYJetsToLL_M_10to50_MLM, DYJetsToLL_M_50_a, WWTo2L2Nu, WZTo2L2Q, ZZTo2L2Nu, ZZTo2L2Q, ZZTo2Q2Nu',
         'data' : 'SingleMuon_2018, EGamma_2018, DoubleMuon_2018, MuonEG_2018',
       }
}

colors = {
 'Charge flips' : kAzure+2,
 'Prompt SS' : kAzure+3,
 'Semileptonic tt' : kRed-9,
 'Other nonprompt': kGray,
 'data' : 1,
}

selection = ''

loopcode = '''
if syst == 'TopPtUp' and self.sampleName == 'TTTo2L2Nu': exprW = t.TWeight_TopPt
values = [%i,  %i, t.TDilep_Pt, t.TDeltaPhi, t.TDeltaEta, t.TLep0Pt, t.TLep0Eta, t.TLep1Pt, vmet, t.TLep1Eta, vmll, vmt2, vht]
prob1 = self.pd1.GetProb(values)
'''%(ms, ml)

 
def GetHistosFromLooper(year, ecut = '(t.TStatus == 1 or t.TStatus == 22)', processes = ['Charge flips','Prompt SS']):
  #l = looper(path=path[year], nSlots = 6, treeName = 'MiniTree', options = 'merge', nEvents = 1000, outpath=outpath+'tempfiles/')
  l = looper(path=path[year], nSlots = 20, treeName = 'MiniTree', options = 'merge', outpath = outpath+'tempfiles/')
  l.AddHeader('from framework.mva import ModelPredict\n')
  l.AddInit('      self.pd1 = ModelPredict("%s")\n'%model)

  for p in processes: l.AddSample(p,  processDic[year][p])

  syst = 'MuonEff, ElecEff, Trig, JES, JER, MuonES, Uncl, Btag, MisTag, PU, TopPt'
  if year != 2018: syst += ', Pref'
  systlist = [x+y for x in syst.replace(' ','').split(',') for y in ['Up','Down']]
  l.AddSyst(systlist)
  l.AddLoopCode(loopcode)

  l.AddExpr('deltaphi', 'TDeltaPhi', 'abs(TDeltaPhi)/3.141592')
  l.AddExpr('deltaeta', 'TDeltaEta', 'abs(TDeltaEta)')
  l.AddExpr('weight1', [], '1')
  l.AddExpr('vpd', '', 'prob1', True) # True because prob1 has to be defined before
  l.AddExpr('vmet', ['TMET'], 'TMET')
  l.AddExpr('vmt2', ['TMT2'], 'TMT2')
  l.AddExpr('vht',  ['THT' ], 'THT')
  l.AddExpr('vmll', ['TMll'], 'TMll')
  l.AddExpr('exprW', ['TWeight'], 'TWeight')

  l.AddSelection(selection)
  weight = 'exprW'
  cut = 'TMET > 50 and TMT2 > 80 and TNJets >= 2 and TNBtags >= 1 and TPassDilep and %s'%ecut
  l.AddCut(cut, ['TMET', 'TMT2', 'TNJets', 'TNBtags', 'TPassDilep'])
  cut = ''

  l.AddHisto('vpd',   'dnn',  20, 0, 1,   weight = weight, cut = '')
  l.AddHisto('TMll', 'mll', 30, 0, 300, weight = weight, cut = '')
  l.AddHisto('TMET', 'met', 25, 50, 300, weight = weight, cut = '')
  l.AddHisto('TMT2', 'mt2', 8, 80, 160, weight = weight, cut = '')
  l.AddHisto('TDilep_Pt', 'dileppt', 30, 0, 300, weight = weight, cut = '')
  l.AddHisto('TLep0Pt', 'lep0pt', 15, 0, 150, weight = weight, cut = '')
  l.AddHisto('TLep1Pt', 'lep1pt', 30, 0, 300, weight = weight, cut = '')
  l.AddHisto('TLep0Eta', 'lep0eta', 30, -2.4, 2.4, weight = weight, cut = '')
  l.AddHisto('TLep1Eta', 'lep1eta', 30, -2.4, 2.4, weight = weight, cut = '')
  l.AddHisto('deltaphi', 'deltaphi', 30, 0, 1, weight = weight, cut = '')
  l.AddHisto('deltaeta', 'deltaeta', 30, 0, 5, weight = weight, cut = '')
  l.AddHisto('TJet0Pt', 'jet0pt', 30, 0, 450, weight = weight, cut = '')
  l.AddHisto('TJet1Pt', 'jet1pt', 30, 0, 300, weight = weight, cut = '')
  l.AddHisto('TJet0Eta', 'jet0eta', 30, -2.4, 2.4, weight = weight, cut = '')
  l.AddHisto('TJet1Eta', 'jet1eta', 30, -2.4, 2.4, weight = weight, cut = '')
  l.AddHisto('THT', 'ht', 40, 0, 800, weight = weight, cut = '')
  l.AddHisto('TNJets', 'njets', 6, 1.5, 7.5, weight = weight, cut = '')
  l.AddHisto('TNBtags', 'nbtags', 3, 0.5, 3.5, weight = weight, cut = '')

  out = l.Run()
  return out

promptSS    = GetHistosFromLooper(year, ecut = 't.TIsSS and (t.TStatus == 1 or  t.TStatus == 22)', processes = ['Charge flips','Prompt SS', 'data'])
nonpromptSS = GetHistosFromLooper(year, ecut = 't.TIsSS and (t.TStatus != 1 and t.TStatus != 22)', processes = ['Semileptonic tt','Other nonprompt'])
nonpromptOS = GetHistosFromLooper(year, ecut = 'not t.TIsSS and (t.TStatus != 1 and t.TStatus != 22)', processes = ['Semileptonic tt','Other nonprompt'])

ss = {}
for k in promptSS   .keys(): ss[k] = promptSS[k]
for k in nonpromptSS.keys(): ss[k] = nonpromptSS[k]

hDDOSdic = {}
for v in vardic.keys(): save(v)
  hDDOS = ss['data'][var].Clone()
  nb = hDDOS.GetNbinsX()
  for ib in range(0, nb+1):
    dataSS   = ss['data'][var].GetBinContent(ib)
    promptSS = ss['Prompt SS'][var].GetBinContent(ib) + ss['Charge flips'][var].GetBinContent(ib)
    mcOS     = nonpromptOS['Semileptonic tt'][var].GetBinContent(ib) + nonpromptOS['Other nonprompt'][var].GetBinContent(ib)
    mcSS     = ss['Semileptonic tt'][var].GetBinContent(ib) + ss['Other nonprompt'][var].GetBinContent(ib)
    ddbin    = (dataSS - promptSS)*(mcOS/mcSS)
    hDDOS.SetBinContent(ib, ddbin)
  hDDOSdic[var] = hDDOS

hm = HistoManager(['Prompt SS', 'Charge flips', 'Other nonprompt', 'Semileptonic tt'], path = path[year], processDic = processDic[year], lumi = GetLumi(year)*1000, indic=ss)

hm = HistoManager(['Prompt SS', 'Charge flips', 'Other nonprompt', 'Semileptonic tt'], path = path[year], processDic = processDic[year], lumi = GetLumi(year)*1000, indic=ss)
def save(name):
  hm.SetHisto(name)
  hm.Save(outname = outpath+'/'+name, htag = '')
  s = Stack(outpath = outpath+'/plots/')
  s.SetColors(colors)
  s.SetProcesses(processes)
  s.SetLumi(GetLumi(year))
  s.SetOutName(name)
  s.SetHistosFromMH(hm)
  s.DrawStack(vardic[name] if name in vardic.keys() else '', 'Events')

for v in vardic.keys(): save(v)



