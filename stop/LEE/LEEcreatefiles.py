'''
 python CreateRootFiles.py -s tt -n 100 --sendJobs --mStop 275 --mLSP 100 #-q short
'''

import os, sys
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)
from stop.config import *
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
parser.add_argument('--year',         default=2018   , help = 'Year')
parser.add_argument('--chan',         default='emu', help = 'Channel')
parser.add_argument('--mStop',        default=275  , help = 'Stop mass')
parser.add_argument('--mLSP',         default=100  , help = 'Neutralino mass')
parser.add_argument('--BS',          action='store_true'  , help = 'Do BS region')
parser.add_argument('--SR',          action='store_true'  , help = 'Do signal region')
parser.add_argument('--scan',        action='store_true'  , help = 'Run scan')
parser.add_argument('--region',       default='SR'  , help = 'Select the region')
parser.add_argument('--sendJobs','-j'   , action='store_true'  , help = 'Send jobs!')

 
#args = parser.parse_args()
args, unknown = parser.parse_known_args()

ms   = int(args.mStop)
ml   = int(args.mLSP)
year = int(args.year)
sendJobs = args.sendJobs
chan = args.chan
scan = args.scan
argprocess = ''
treeName="MiniTree"
nSlots = 1

baseoutpath +='/LEE/'
webpath     +='/LEE/'
path = {
  2016:'/pool/phedexrw/userstorage/juanr/stopLEE/23apr/2016/',
  2017:'/pool/phedexrw/userstorage/juanr/stopLEE/23apr/2017/',
  2018:'/pool/phedexrw/userstorage/juanr/stopLEE/23apr/2018/',
}

processDic = {
       2018 : {
          'tt_test'  : 'TTTo2L2Nu_test',
          #'tt'  : 'TTTo2L2Nu',
          'tW'  : 'tbarW_noFullHad, tW_noFullHad',
          'ttZ' : 'TTZToLL_M_1to10, TTZToLLNuNu_M_10_a, TTZToQQ',
          'Nonprompt' : 'TTToSemiLeptonic, WJetsToLNu_MLM,TTTo2L2Nu,tbarW_noFullHad, tW_noFullHad,WWTo2L2Nu, WZTo2L2Q, WZTo3LNu, ZZTo2L2Nu, ZZTo2L2Q, ZZTo4L',
          'Others'     : 'TTWJetsToLNu, TTWJetsToQQ, DYJetsToLL_M_10to50_MLM, DYJetsToLL_M_50_a, WWTo2L2Nu, WZTo2L2Q, WZTo3LNu, ZZTo2L2Nu, ZZTo2L2Q, ZZTo4L',
        },
        2017 : {
          'tt_test'  : 'TTTo2L2Nu_test',
          #'tt'  : 'TTTo2L2Nu',
          'tW'  : 'tbarW_noFullHad, tW_noFullHad',
          'ttZ' : 'TTZToLL_M_1to10, TTZToLLNuNu_M_10_a, TTZToQQ',
          'Nonprompt' : 'TTToSemiLeptonic, WJetsToLNu_MLM,TTTo2L2Nu,tbarW_noFullHad, tW_noFullHad,WWTo2L2Nu, WZTo2L2Q, WZTo3LNu, ZZTo2L2Nu, ZZTo2L2Q, ZZTo4L',
          'Others'     : 'TTWJetsToLNu, TTWJetsToQQ, DYJetsToLL_M_10to50_MLM, DYJetsToLL_M_50_a, WWTo2L2Nu, WZTo2L2Q, WZTo3LNu, ZZTo2L2Nu, ZZTo2L2Q, ZZTo4L',
        },
    		2016 : {
          'tt_test'  : 'TT_test',
          #'tt'  : 'TT',
          'tW'  : 'tbarW_noFullHad, tW_noFullHad',
          'ttZ' : 'TTZToLL_M_1to10_MLM, TTZToLLNuNu_M_10_a,TTZToQQ',#, TTZToQQ',
          'Nonprompt' : 'TTToSemiLeptonic, WJetsToLNu_MLM, TT, tbarW_noFullHad, tW_noFullHad, WWTo2L2Nu, WZTo2L2Q, WZTo3LNu, ZZTo2L2Nu, ZZTo2L2Q, ZZTo4L',
          'Others'     : 'TTWJetsToLNu, TTWJetsToQQ,DYJetsToLL_M_10to50, DYJetsToLL_M_50_a, WWTo2L2Nu, WZTo2L2Q, WZTo3LNu, ZZTo2L2Nu, ZZTo2L2Q, ZZTo4L',
        }
}
 

# Set signal masses
#ms = 275
#ml = 100
region = args.region
if args.BS: region = 'BS'
if args.SR: region = 'SR'

if chan in ['ee', 'mumu']:
  path[year] = pathsf(year, chan, region)
  folder = folder+'_'+chan
  baseoutpath = '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/'+folder
  webpath  = '/nfs/fanae/user/juanr/www/stopLegacy/nanoAODv6/'+folder

# Set constants
outpath = baseoutpath+'/Unc/%s/%i/mass%i_%i/'%(region, year, ms, ml)
os.system("mkdir -p %s"%outpath)

if not sendJobs:
  processes.append('stop_test')
  for year in [2016, 2017, 2018]: processDic[year]['stop_test'] = ''

# Create the looper, set readOutput to true to read previous temporary rootfiles created for each sample
l = looper(path=path[year] if region=='SR' else pathBS[year], nSlots=nSlots, treeName = 'MiniTree', options = 'merge', outpath = outpath+'tempfiles/', readOutput=True)#, sendJobs=sendJobs)

# Add processes
processes = processDic[year].keys() #['tt']
if argprocess != '': processes = argprocess
for p in processes: l.AddSample(p,  processDic[year][p])

nToys = 100
# Systematic uncertainties
syst = 'JESCor, JESUnCor, JER, Uncl, PU'#, MuonEff, ElecEff, TrigEff, MuonES, ElecES, Btag, MisTag, TopPt, UE, hdamp, mtop'

if year != 2018: syst += ', Pref'
if year != 2016: syst += ', ISR, FSR'
# PDF, ME, nongauss
systlist = [x+y for x in syst.replace(' ','').split(',') for y in ['Up','Down']]
#for i in range(nToys): systlist += ['NormToy%i'%i]

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
 if self.outname.startswith('stop'):
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
l.AddHisto('TMll', 'mll', 30, 0, 300, weight = weight, cut = '')
l.AddHisto('TMET', 'met', 25, 50, 300, weight = weight, cut = '')
l.AddHisto('TMT2', 'mt2', 8, 80, 160, weight = weight, cut = '')
histos = ['mt2',  'met',  'mll',  'dnn']

if scan:
  stopmasses = GetAllStopNeutralinoPoints(mode='diag')
  for year in [2018]:#[2016, 2017, 2018]:#, 2017, 2018]:
    for sm, nm in stopmasses:
      if sendJobs:
        os.system('python LEEcreatefiles.py --year %i --mStop %i --mLSP %i -s tt_test -n 100 --sendJobs'%(year, sm, nm))
        os.system('python LEEcreatefiles.py --year %i --mStop %i --mLSP %i -s tW -n 10 --sendJobs'%(year, sm, nm))
        os.system('python LEEcreatefiles.py --year %i --mStop %i --mLSP %i -s ttZ -n 10 --sendJobs'%(year, sm, nm))
        os.system('python LEEcreatefiles.py --year %i --mStop %i --mLSP %i -s Nonprompt -n 10 --sendJobs'%(year, sm, nm))
        os.system('python LEEcreatefiles.py --year %i --mStop %i --mLSP %i -s Others -n 10 --sendJobs'%(year, sm, nm))
      else: os.system('python LEEcreatefiles.py --year %i --mStop %i --mLSP %i'%(year, sm, nm))
  exit()

out = l.Run()

if sendJobs: exit()
# Create HistoManager with the out dictionary from the looper
if 'data' in processes: processes.pop(processes.index('data'))
hm = HistoManager(processes, path = path[year] if region == 'SR' else pathBS[year], processDic = processDic[year], lumi = GetLumi(year)*1000,indic = out)

# Function to save the histograms into combine rootfiles
def save(name):
  hm.SetHisto(name)
  hm.Save(outname = outpath+'/'+name, htag = '')

# Save the histograms

for v in histos: save(v)
