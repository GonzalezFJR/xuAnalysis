'''
 python CreateRootFiles.py -s tt -n 100 --sendJobs --mStop 275 --mLSP 100 #-q short
'''

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
import argparse

parser = argparse.ArgumentParser(description='To select masses and year')
parser.add_argument('--year','-y',    default=2018   , help = 'Year')
parser.add_argument('--mStop',        default=275  , help = 'Stop mass')
parser.add_argument('--mLSP',         default=100  , help = 'Neutralino mass')
parser.add_argument('--BS',          action='store_true'  , help = 'Do BS region')
parser.add_argument('--SR',          action='store_true'  , help = 'Do signal region')
parser.add_argument('--region',       default='SR'  , help = 'Select the region')
parser.add_argument('--channel','-c', default='emu'  , help = 'Select the channel')
parser.add_argument('--sendJobs','-j'   , action='store_true'  , help = 'Send jobs!')

 
#args = parser.parse_args()
args, unknown = parser.parse_known_args()

ms   = int(args.mStop)
ml   = int(args.mLSP)
year = int(args.year)
sendJobs = args.sendJobs
chan = args.channel
#nSlots = args.nSlots
#argprocess = args.process
#if   ',' in argprocess: argprocess = argprocess.replace(' ', '').split(',')
#elif argprocess != '' : argprocess = [argprocess]
argprocess = ''
treeName="MiniTree"
nSlots = 1

# Set signal masses
#ms = 275
#ml = 100
region = args.region
if args.BS: region = 'BS'
if args.SR: region = 'SR'

path = {}
path[year] = pathToTrees(year, chan, region)

if chan in ['ee', 'mumu']:
  for y in [2016, 2017, 2018]:
    processDic[y]['stop_test'] = 'stop'
    processDic[y]['tt_test'] = 'TTTo2L2Nu' if y != 2016 else 'TT'


# Set constants
outpath = baseoutpath+'/Unc/%s/%s/%i/mass%i_%i/'%(region, chan, year, ms, ml)
os.system("mkdir -p %s"%outpath)

# Create the looper, set readOutput to true to read previous temporary rootfiles created for each sample
l = looper(path=path[year] if region=='SR' else pathBS[year], nSlots=nSlots, treeName = 'MiniTree', options = 'merge', outpath = outpath+'tempfiles/', readOutput=True)#, sendJobs=sendJobs)

# Add processes
processes = processDic[year].keys() #['tt']
if argprocess != '': processes = argprocess
for p in processes: l.AddSample(p,  processDic[year][p])

# Systematic uncertainties
syst = 'MuonEff, ElecEff, Trig, JESCor, JESUnCor, JER, MuonES, ElecES, Uncl, Btag, MisTag, PU, TopPt, UE, hdamp, mtop'

if year != 2018: syst += ', Pref'
if year != 2016: syst += ', ISR, FSR'
# PDF, ME, nongauss
systlist = [x+y for x in syst.replace(' ','').split(',') for y in ['Up','Down']]

# Lines below to read the DNN values
l.AddHeader('from framework.mva import ModelPredict\n')
l.AddInit('      self.pd1 = ModelPredict("%s")\n'%model)
l.AddInit("      if self.outname in ['ttnongauss', 'tt_hdampUp', 'tt_hdampDown', 'tt_UEUp', 'tt_UEDown', 'tt_mtopUp', 'tt_mtopDowm', 'data', 'data_obs', 'Data']: self.systematics = ['']\n")
l.AddSyst(systlist)
loopcode = '''
values = [%i,  %i, t.TDilep_Pt, t.TDeltaPhi, t.TDeltaEta, t.TLep0Pt, t.TLep0Eta, t.TLep1Pt, vmet, t.TLep1Eta, vmll, vmt2, vht]
prob1 = self.pd1.GetProb(values)
'''%(ms, ml)
l.AddLoopCode(loopcode)

# Select the signal and add cut in masses (in principle, one signal at a time)
stopcutline = lambda signal, mstop, mlsp : '   if not (mStop == %s and mLSP == %s ): return\n'%( mstop, mlsp)
massfromsig = lambda signal : signal[4:].split('_')
stopcuts = ''
for sig in ['stop%i_%i'%(ms, ml)]:
  mstop, mlsp = massfromsig(sig)
  stopcuts += stopcutline(sig, mstop, mlsp)

hemsel = '''
 if self.outname == 'ttnoHEM':
   if t.TIsHEM: return
'''
selection = '''
 if self.outname in ['stop', 'stop_test']:
   mStop = t.Tm_stop; mLSP = t.Tm_LSP%s
 elif self.outname == 'Nonprompt':
   passNonprompt = (t.TStatus != 1 and t.TStatus != 22)
   if not passNonprompt: return 
 elif self.outname != 'data':
   passNonprompt = (t.TStatus == 1 or  t.TStatus == 22)
   if not passNonprompt: return 
 if self.outname == 'ttnongauss':
   if t.TJERindex != 2:  return
%s 
'''%('\n'+stopcuts+'\n', hemsel if year == 2018 else '')
l.AddSelection(selection)


# Define expresions, including varibles with syst variations
l.AddExpr('deltaphi', 'TDeltaPhi', 'abs(TDeltaPhi)/3.141592')
l.AddExpr('deltaeta', 'TDeltaEta', 'abs(TDeltaEta)')
l.AddExpr('weight1', [], '1')
l.AddExpr('exprW', ['TWeight'], 'TWeight')
l.AddExpr('vmet', ['TMET'], 'TMET')
l.AddExpr('vmt2', ['TMT2'], 'TMT2')
l.AddExpr('vmt2lblb', ['TMT2lblb'], 'TMT2lblb')
l.AddExpr('vht',  ['THT' ], 'THT')
l.AddExpr('vmll', ['TMll'], 'TMll')
l.AddExpr('vpd', '', 'prob1', True)

# Weight and cuts...
l.AddCut('t.TIsSS == 0', [])
l.AddCut('TPassDilep == 1', 'TPassDilep')
if region == 'SR':
  l.AddCut('TMET >= 50', 'TMET')
  l.AddCut('TMT2 >= 80', 'TMT2')
elif region == 'ttMET' or region == 'ttmet':
  l.AddCut('TMT2 < 80', 'TMT2')
elif region == 'ttMT2' or region == 'ttmt2':
  l.AddCut('TMET < 50', 'TMET')
elif region == 'CR':
  l.AddCut('(TMET < 50 and TMT2 < 80)', ['TMET', 'TMT2'])
l.AddCut('TNJets >= 2', 'TNJets')
l.AddCut('TNBtags >= 1', 'TNBtags')
# Add histograms
cut = ''
weight = 'exprW'
l.AddHisto('vpd',  'dnn',  20, 0, 1,   weight = weight, cut = '')
l.AddHisto('vpd',  'dnnVIPS',  bins=[0.  , 0.05, 0.1 , 0.15, 0.2 , 0.25, 0.3 , 0.35, 0.4 , 0.45, 0.5 ,0.55, 0.6 , 0.65, 0.7 , 0.75, 0.8 , 0.85, 0.9 , 0.95, 0.98, 1.0],   weight = weight, cut = '')
l.AddHisto('vpd',  'dnn_10bins',  10, 0, 1,   weight = weight, cut = '')
l.AddHisto('vpd',  'dnn_30bins',  30, 0, 1,   weight = weight, cut = '')
l.AddHisto('vpd',  'dnn_40bins',  40, 0, 1,   weight = weight, cut = '')
l.AddHisto('vpd',  'dnn_5bins',  5, 0, 1,   weight = weight, cut = '')
l.AddHisto('TMll', 'mll', 30, 0, 300, weight = weight, cut = '')
l.AddHisto('TMT2lblb', 'mtwlblb', 30, 0, 300, weight = weight, cut = '')
if region == 'SR':
  l.AddHisto('TMET', 'met', 25, 50, 300, weight = weight, cut = '')
  l.AddHisto('TMET', 'met_5bins', 5, 50, 300, weight = weight, cut = '')
  l.AddHisto('TMT2', 'mt2', 8, 80, 160, weight = weight, cut = '')
  l.AddHisto('TMT2', 'mt2_4bins', 4, 80, 160, weight = weight, cut = '')
  l.AddHisto('TMT2', 'mt2_3bins', 3, 80, 160, weight = weight, cut = '')
  l.AddHisto('TMT2', 'mt2_2bins', 2, 80, 160, weight = weight, cut = '')
  l.AddHisto('TMT2',     'mt2_dnng80',     8,  80, 160, weight = weight, cut = 'vpd>0.80')
  l.AddHisto('TMET',     'met_dnng80',     25, 50, 300, weight = weight, cut = 'vpd>0.80')
  l.AddHisto('TMT2lblb', 'mt2lblb_dnng80', 25, 50, 300, weight = weight, cut = 'vpd>0.80')
  l.AddHisto('TMT2',     'mt2_dnng90',     8,  80, 160, weight = weight, cut = 'vpd>0.90')
  l.AddHisto('TMET',     'met_dnng90',     25, 50, 300, weight = weight, cut = 'vpd>0.90')
  l.AddHisto('TMT2lblb', 'mt2lblb_dnng90', 25, 50, 300, weight = weight, cut = 'vpd>0.90')
  l.AddHisto('TMT2',     'mt2_dnng95',     8,  80, 160, weight = weight, cut = 'vpd>0.95')
  l.AddHisto('TMET',     'met_dnng95',     25, 50, 300, weight = weight, cut = 'vpd>0.95')
  l.AddHisto('TMT2lblb', 'mt2lblb_dnng95', 25, 50, 300, weight = weight, cut = 'vpd>0.95')

else:
  l.AddHisto('TMET', 'met', 30, 0, 300, weight = weight, cut = '')
  l.AddHisto('TMT2', 'mt2', 16, 0, 160, weight = weight, cut = 'vmt2 > 0')
l.AddHisto('TDilep_Pt', 'dileppt', 30, 0, 300, weight = weight, cut = '')
l.AddHisto('TLep0Pt', 'lep0pt', 20, 0, 200, weight = weight, cut = '')
l.AddHisto('TLep1Pt', 'lep1pt', 15, 0, 150, weight = weight, cut = '')
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

l.AddHisto('TMET', 'met_dnng0p95', 5, 50, 300, weight = weight, cut = 'vpd>0.95')
l.AddHisto('TMT2', 'mt2_dnng0p95', 4, 80, 160, weight = weight, cut = 'vpd>0.95')
l.AddHisto('TMET', 'met_dnng0p90', 5, 50, 300, weight = weight, cut = 'vpd>0.90')
l.AddHisto('TMT2', 'mt2_dnng0p90', 4, 80, 160, weight = weight, cut = 'vpd>0.90')
'''
l.AddHisto('TDilep_Pt', 'dileppt_dnng0p95', 6, 0, 300, weight = weight, cut = 'vpd>0.95')
l.AddHisto('TLep0Pt', 'lep0pt_dnng0p95', 9, 20, 200, weight = weight, cut = 'vpd>0.95')
l.AddHisto('TLep1Pt', 'lep1pt_dnng0p95', 6, 20, 140, weight = weight, cut = 'vpd>0.95')
l.AddHisto('TLep0Eta', 'lep0eta_dnng0p95', 8, -2.4, 2.4, weight = weight, cut = 'vpd>0.95')
l.AddHisto('TLep1Eta', 'lep1eta_dnng0p95', 8, -2.4, 2.4, weight = weight, cut = 'vpd>0.95')
l.AddHisto('deltaphi', 'deltaphi_dnng0p95', 5, 0, 1, weight = weight, cut = 'vpd>0.95')
l.AddHisto('deltaeta', 'deltaeta_dnng0p95', 5, 0, 5, weight = weight, cut = 'vpd>0.95')
l.AddHisto('TJet0Pt', 'jet0pt_dnng0p95', 9, 0, 450, weight = weight, cut = 'vpd>0.95')
l.AddHisto('THT', 'ht_dnng0p95', 8, 0, 800, weight = weight, cut = 'vpd>0.95')
l.AddHisto('TNJets', 'njets_dnng0p95', 6, 1.5, 7.5, weight = weight, cut = 'vpd>0.95')
l.AddHisto('TNBtags', 'nbtags_dnng0p95', 3, 0.5, 3.5, weight = weight, cut = 'vpd>0.95')

l.AddHisto('TDilep_Pt', 'dileppt_dnng0p90', 6, 0, 300, weight = weight, cut = 'vpd>0.90')
l.AddHisto('TLep0Pt', 'lep0pt_dnng0p90', 9, 20, 200, weight = weight, cut = 'vpd>0.90')
l.AddHisto('TLep1Pt', 'lep1pt_dnng0p90', 6, 20, 140, weight = weight, cut = 'vpd>0.90')
l.AddHisto('TLep0Eta', 'lep0eta_dnng0p90', 8, -2.4, 2.4, weight = weight, cut = 'vpd>0.90')
l.AddHisto('TLep1Eta', 'lep1eta_dnng0p90', 8, -2.4, 2.4, weight = weight, cut = 'vpd>0.90')
l.AddHisto('deltaphi', 'deltaphi_dnng0p90', 5, 0, 1, weight = weight, cut = 'vpd>0.90')
l.AddHisto('deltaeta', 'deltaeta_dnng0p90', 5, 0, 5, weight = weight, cut = 'vpd>0.90')
l.AddHisto('TJet0Pt', 'jet0pt_dnng0p90', 9, 0, 450, weight = weight, cut = 'vpd>0.90')
l.AddHisto('THT', 'ht_dnng0p90', 8, 0, 800, weight = weight, cut = 'vpd>0.90')
l.AddHisto('TNJets', 'njets_dnng0p90', 6, 1.5, 7.5, weight = weight, cut = 'vpd>0.90')
l.AddHisto('TNBtags', 'nbtags_dnng0p90', 3, 0.5, 3.5, weight = weight, cut = 'vpd>0.90')
'''

histos = ['mt2',  'met',  'mll',  'dnn',  'dileppt',  'deltaphi',  'deltaeta',  'ht',  'lep0pt',  'lep1pt',  'lep0eta',  'lep1eta', 'njets', 'nbtags', 'jet0pt', 'jet1pt', 'jet0eta', 'jet1eta']#, 'mtwlblb'] 
#histos += ['dnn_10bins', 'dnn_30bins', 'dnn_40bins'] #histos += ['dnnVIPS']#
#histos += ['dnn_5bins', 'dnn_10bins', 'dnn_30bins', 'dnn_40bins'] #histos += ['dnnVIPS']#
#histos += ['met_dnng0p95', 'mt2_dnng0p95', 'met_dnng0p90', 'mt2_dnng0p90']
#histos += ['met_dnng0p95', 'mt2_dnng0p95', 'dileppt_dnng0p95', 'lep0pt_dnng0p95', 'lep0pt_dnng0p95', 'lep1pt_dnng0p95', 'lep0eta_dnng0p95', 'lep1eta_dnng0p95', 'deltaphi_dnng0p95', 'deltaeta_dnng0p95', 'jet0pt_dnng0p95', 'ht_dnng0p95', 'njets_dnng0p95', 'nbtags_dnng0p95']
#histos += ['met_dnng0p90', 'mt2_dnng0p90', 'dileppt_dnng0p90', 'lep0pt_dnng0p90', 'lep0pt_dnng0p90', 'lep1pt_dnng0p90', 'lep0eta_dnng0p90', 'lep1eta_dnng0p90', 'deltaphi_dnng0p90', 'deltaeta_dnng0p90', 'jet0pt_dnng0p90', 'ht_dnng0p90', 'njets_dnng0p90', 'nbtags_dnng0p90']
#if region=='SR': histos += ['mt2_dnng80', 'met_dnng80', 'mt2lblb_dnng80', 'mt2_dnng90', 'met_dnng90', 'mt2lblb_dnng90', 'mt2_dnng95', 'met_dnng95', 'mt2lblb_dnng9']

'''
# Scan in MET
for val in arange(50, 300, 10):
  hname = 'metScanstop%i_%i_%1.0f'%(ms,ml,val*100)
  histos.append(hname)
  l.AddHisto('weight1', hname,  1, -1, 20,   weight = weight, cut = 'vmet > %1.2f'%val)
# Scan in DNN
for val in arange(0.5, 1, 0.05):
  hname = 'dnnScanstop%i_%i_%1.0f'%(ms,ml,val*100)
  histos.append(hname)
  l.AddHisto('weight1', hname,  1, -1, 20,   weight = weight, cut = 'vpd > %1.2f'%val)
'''
 
out = l.Run()

if sendJobs: exit()
# Create HistoManager with the out dictionary from the looper
processes.pop(processes.index('data'))
#print 'processes: ', processes
hm = HistoManager(processes, path = path[year] if region == 'SR' else pathBS[year], processDic = processDic[year], lumi = GetLumi(year)*1000.,indic = out)

# Function to save the histograms into combine rootfiles
def save(name):
  hm.SetHisto(name)
  hm.Save(outname = outpath+'/'+name, htag = '')

# Save the histograms
for v in histos: save(v)

