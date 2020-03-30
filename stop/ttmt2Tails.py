import os, sys
#from config import *
from config import GetLumi, path, pathBS
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)
from plotter.TopHistoReader import TopHistoReader, HistoManager
from plotter.Plotter import Stack, HistoComp
from framework.looper import looper
from ROOT.TMath import Sqrt as sqrt
from ROOT import kRed, kOrange, kBlue, kTeal, kGreen, kGray, kAzure, kPink, kCyan, kBlack, kSpring, kViolet, kYellow
from ROOT import TCanvas, gROOT, TLegend, TCanvas
gROOT.SetBatch(1)
import argparse

parser = argparse.ArgumentParser(description='To select masses and year')
parser.add_argument('--year',         default='2018'   , help = 'Year')
parser.add_argument('--mStop',        default=275  , help = 'Stop mass')
parser.add_argument('--mLSP',         default=100  , help = 'Neutralino mass')
parser.add_argument('--BS',          action='store_true'  , help = 'Do BS region')
parser.add_argument('--SR',          action='store_true'  , help = 'Do signal region')
parser.add_argument('--sendJobs','-j'   , action='store_true'  , help = 'Send jobs!')
 
#args = parser.parse_args()
args, unknown = parser.parse_known_args()

ms   = int(args.mStop)
ml   = int(args.mLSP)
year = int(args.year) if args.year.isdigit() else args.year
sendJobs = args.sendJobs



region = 'SR'
if args.BS: region = 'BS'
if args.SR: region = 'SR'
treeName="MiniTree"
syst = 'MuonEff, ElecEff, Trig, JER, MuonES, Uncl, Btag, MisTag, PU, JESCor, JESUnCor, ElecES'
if year != 2018: syst += ', Pref'
systlist = [x+y for x in syst.replace(' ','').split(',') for y in ['Up','Down']]

GetOutPath = lambda year, region : '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/stop/ttmt2/%s/%s/'%(str(year), region)
outpath = GetOutPath(year, region) 
model = '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/TopPlots/DrawMiniTrees/NNtotal_model2.h5'

vardic = {
'mt2'      : 'm_{T2} (GeV)',
'mt2_4bins': 'm_{T2} (GeV)',
'met'      : 'MET (GeV)',
'mll'      : 'm_{e#mu} (GeV)',
'dnn_5'    : 'DNN score',
'dnn_10'   : 'DNN score',
'dnn'      : 'DNN score',
'count'    : 'Counts',
'dileppt'  : 'p_{T}^{e#mu} (GeV)',
'deltaphi' : '#Delta#phi (rad/#pi)',
'deltaeta' : '#Delta#eta',
'ht'       : 'H_{T} (GeV)',
'lep0pt'   : 'Leading lepton p_{T} (GeV)',
'lep1pt'   : 'Subleading lepton p_{T} (GeV)',
'lep0eta'  : 'Leading lepton #eta',
'lep1eta'  : 'Subleading lepton #eta',
'njets'    : 'Jet multiplicity',
'nbtags'   : 'b-tag multiplicity',
}
#vardic = { 'nbtags'    : 'b-tag multiplicity'}

processDic = {
2018 : {
       'stop'       : 'stop',
       'tt'         : 'TTTo2L2Nu',
       'ttgaus'     : 'TTTo2L2Nu',
       'ttnongaus'  : 'TTTo2L2Nu',
       'tW'  : 'tbarW_noFullHad, tW_noFullHad',
       'ttZ' : 'TTZToLL_M_1to10, TTZToLLNuNu_M_10_a, TTZToQQ',
       'Semileptonictt' : 'TTToSemiLeptonic',
       'ttDilepNonprompt':'TTTo2L2Nu',
       'tWnonprompt':'tbarW_noFullHad, tW_noFullHad',
       'Othernonprompt':'WJetsToLNu_MLM, DYJetsToLL_M_10to50_MLM, DYJetsToLL_M_50_a, WWTo2L2Nu, WZTo2L2Q, ZZTo2L2Nu, ZZTo2L2Q',
       'Others'     : 'TTWJetsToLNu, TTWJetsToQQ, DYJetsToLL_M_10to50_MLM, DYJetsToLL_M_50_a, WWTo2L2Nu, WZTo2L2Q, WZTo3LNu, ZZTo2L2Nu, ZZTo2L2Q, ZZTo4L',
       'tt_hdampUp' : 'TTTo2L2Nu_hdampUp',
       'tt_UEUp'  : 'TTTo2L2Nu_TuneCP5Up',
       'tt_hdampDown' : 'TTTo2L2Nu_hdampDown',
       'tt_UEDown'  : 'TTTo2L2Nu_TuneCP5Down',
       'tt_mtopDown'  : 'TTTo2L2Nu_mtop171p5',
       'tt_mtopUp'  : 'TTTo2L2Nu_mtop173p5',
       'data' : 'EGamma_2018, MuonEG_2018, SingleMuon_2018',
     },
2017 : {
       'tt'  : 'TTTo2L2Nu',
       'ttgaus'     : 'TTTo2L2Nu',
       'ttnongaus'  : 'TTTo2L2Nu',
       'stop'      : 'stop',
       'tW'  : 'tbarW_noFullHad, tW_noFullHad',
       'ttZ' : 'TTZToLL_M_1to10, TTZToLLNuNu_M_10_a, TTZToQQ',
       'Semileptonictt' : 'TTToSemiLeptonic',
       'ttDilepNonprompt':'TTTo2L2Nu',
       'tWnonprompt':'tbarW_noFullHad, tW_noFullHad',
       'Othernonprompt':'WJetsToLNu_MLM, DYJetsToLL_M_10to50_MLM, DYJetsToLL_M_50_a, WWTo2L2Nu, WZTo2L2Q, ZZTo2L2Nu, ZZTo2L2Q',
       'Others'     : 'TTWJetsToLNu, TTWJetsToQQ, DYJetsToLL_M_10to50_MLM, DYJetsToLL_M_50_a, WWTo2L2Nu, WZTo2L2Q, WZTo3LNu, ZZTo2L2Nu, ZZTo2L2Q, ZZTo4L',
       'tt_hdampUp' : 'TTTo2L2Nu_hdampUp',
       'tt_UEUp'  : 'TTTo2L2Nu_TuneCP5Up',
       'tt_hdampDown' : 'TTTo2L2Nu_hdampDown',
       'tt_UEDown'  : 'TTTo2L2Nu_TuneCP5Down',
       'tt_mtopDown'  : 'TTTo2L2Nu_mtop171p5',
       'tt_mtopUp'  : 'TTTo2L2Nu_mtop173p5',
       'data' : 'MuonEG_2017,SingleElectron_2017,SingleMuon_2017',
     },
2016 : {
    'tt'  : 'TT',
    'ttgaus'     : 'TT',
    'ttnongaus'  : 'TT',
    'stop'      : 'stop',
    'tW'  : 'tbarW_noFullHad, tW_noFullHad',
    'ttZ' : 'TTZToLL_M_1to10_MLM, TTZToLLNuNu_M_10_a,TTZToQQ',#, TTZToQQ',
    'Semileptonictt' : 'TTToSemiLeptonic',
    'ttDilepNonprompt':'TT',
    'tWnonprompt':'tbarW_noFullHad, tW_noFullHad',
    'Othernonprompt':'DYJetsToLL_M_10to50, DYJetsToLL_M_50_a, WWTo2L2Nu, WZTo2L2Q, ZZTo2L2Nu, ZZTo2L2Q',
    'Others'     : 'TTWJetsToLNu, TTWJetsToQQ,DYJetsToLL_M_10to50, DYJetsToLL_M_50_a, WWTo2L2Nu, WZTo2L2Q, WZTo3LNu, ZZTo2L2Nu, ZZTo2L2Q, ZZTo4L',
    'data' : 'MuonEG_2016,SingleElectron_2016,SingleMuon_2016',#,DoubleEG_2017,DoubleMuon_2017',
      },
}

stopcutline = lambda signal, mstop, mlsp : '   if not (mStop == %s and mLSP == %s ): return\n'%( mstop, mlsp)
massfromsig = lambda signal : signal[4:].split('_')
stopcuts = ''
for sig in ['stop%i_%i'%(ms, ml)]:
  mstop, mlsp = massfromsig(sig)
  stopcuts += stopcutline(sig, mstop, mlsp)
selection = '''
 if self.outname.startswith('stop'):
   mStop = t.Tm_stop; mLSP = t.Tm_LSP%s
 if self.outname in ['Semileptonictt', 'ttDilepNonprompt', 'tWnonprompt', 'Othernonprompt']:
   passNonprompt = (t.TStatus != 1 and t.TStatus != 22)
   if not passNonprompt: return 
 elif self.outname != 'data':
   passNonprompt = (t.TStatus == 1 or  t.TStatus == 22)
   if not passNonprompt: return 
 if   self.outname == 'tt':
   if t.TJERindex != 0: return 
 elif self.outname == 'ttgaus':
   if t.TJERindex != 1: return 
 elif self.outname == 'ttnongaus':
   if t.TJERindex != 2:  return 
'''%('\n'+stopcuts+'\n')


loopcode = '''
values = [%i,  %i, t.TDilep_Pt, t.TDeltaPhi, t.TDeltaEta, t.TLep0Pt, t.TLep0Eta, t.TLep1Pt, vmet, t.TLep1Eta, vmll, vmt2, vht]
prob1 = self.pd1.GetProb(values)
'''%(ms, ml)

l = looper(path=path[year] if not region=='BS' else pathBS[year], nSlots = 4, treeName = 'MiniTree', options = 'merge', outpath = GetOutPath(year, region)+'/tempfiles/', readOutput=True)
l.AddHeader('from framework.mva import ModelPredict\n')
l.AddInit('      self.pd1 = ModelPredict("%s")\n'%model)

processes = processDic[year].keys() #['tt']
for p in processes: l.AddSample(p,  processDic[year][p])

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
l.AddCut('TPassDilep == 1', 'TPassDilep')
if region != 'BS':
  l.AddCut('TMET >= 50', 'TMET')
  l.AddCut('TMT2 >= 80', 'TMT2')
l.AddCut('TNJets >= 2', 'TNJets')
l.AddCut('TNBtags >= 1', 'TNBtags')
cut = ''

l.AddHisto('vpd',   'dnn_5',  5, 0, 1,   weight = weight, cut = '')
l.AddHisto('vpd',   'dnn_10', 10, 0, 1,   weight = weight, cut = '')
l.AddHisto('vpd',   'dnn', 20, 0, 1,   weight = weight, cut = '')
l.AddHisto('vpd',   'count',  1, 0, 2,   weight = weight, cut = '')
l.AddHisto('TMll', 'mll', 10, 0, 300, weight = weight, cut = '')
l.AddHisto('TMET', 'met', 10, 50, 300, weight = weight, cut = '')
l.AddHisto('TMT2', 'mt2', 8, 80, 160, weight = weight, cut = '')
l.AddHisto('TMT2', 'mt2_4bins', 4, 80, 160, weight = weight, cut = '')
l.AddHisto('TDilep_Pt', 'dileppt', 10, 0, 300, weight = weight, cut = '')
l.AddHisto('TLep0Pt', 'lep0pt', 5, 0, 150, weight = weight, cut = '')
l.AddHisto('TLep1Pt', 'lep1pt', 10, 0, 300, weight = weight, cut = '')
l.AddHisto('TLep0Eta', 'lep0eta', 8, -2.4, 2.4, weight = weight, cut = '')
l.AddHisto('TLep1Eta', 'lep1eta', 8, -2.4, 2.4, weight = weight, cut = '')
l.AddHisto('deltaphi', 'deltaphi', 8, 0, 1, weight = weight, cut = '')
l.AddHisto('deltaeta', 'deltaeta', 8, 0, 5, weight = weight, cut = '')
l.AddHisto('TJet0Pt', 'jet0pt', 10, 0, 450, weight = weight, cut = '')
l.AddHisto('TJet1Pt', 'jet1pt', 6, 0, 300, weight = weight, cut = '')
l.AddHisto('TJet0Eta', 'jet0eta', 8, -2.4, 2.4, weight = weight, cut = '')
l.AddHisto('TJet1Eta', 'jet1eta', 8, -2.4, 2.4, weight = weight, cut = '')
l.AddHisto('THT', 'ht', 8, 0, 800, weight = weight, cut = '')
l.AddHisto('TNJets', 'njets', 6, 1.5, 7.5, weight = weight, cut = '')
l.AddHisto('TNBtags', 'nbtags', 3, 0.5, 3.5, weight = weight, cut = '')
histos  = ['mt2',  'met',  'mll',  'dnn',  'dileppt',  'deltaphi',  'deltaeta',  'ht',  'lep0pt',  'lep1pt',  'lep0eta',  'lep1eta', 'njets', 'nbtags', 'jet0pt', 'jet1pt', 'jet0eta', 'jet1eta'] 

out = l.Run()

if sendJobs: exit()

# Create HistoManager with the out dictionary from the looper
processes.pop(processes.index('data'))
hm = HistoManager(processes, path = path[year] if region == 'SR' else pathBS[year], processDic = processDic[year], lumi = GetLumi(year)*1000,indic = out)

# Function to save the histograms into combine rootfiles
def save(name):
  hm.SetHisto(name)
  hm.Save(outname = outpath+'/'+name, htag = '')

# Save the histograms
for v in histos: save(v)
