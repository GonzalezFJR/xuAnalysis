'''
 python CreateRootFiles.py -s tt -n 100 --sendJobs --mStop 275 --mLSP 100 #-q short
'''

import os, sys
from config import *
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)
from plotter.TopHistoReader import TopHistoReader, HistoManager
from plotter.Plotter import Stack, HistoUnc
from framework.looper import looper
from ROOT.TMath import Sqrt as sqrt
from ROOT import kRed, kOrange, kBlue, kTeal, kGreen, kGray, kAzure, kPink, kCyan, kBlack, kSpring, kViolet, kYellow
from ROOT import TCanvas, gROOT, TLegend, TFile
from numpy import arange
gROOT.SetBatch(1)

from math import sqrt
def GetPDFuncHisto(nom, pdfvars, alphasvar = [], prName = 'tt'):
  # Using PDF4LHC15_nlo_nf4_30_pdfas, 1+30+2 weights, see Table 6 in 
  # https://arxiv.org/pdf/1510.03865.pdf
  # Eq [20] for PDF unc:  0.01 (0.45 %)
  # Eq [27] for alpha_S:  0.00 (0.15 %)
  nom.SetName(prName)
  nbins = nom.GetNbinsX()+1
  up = nom.Clone(prName+'_PDFUp')
  do = nom.Clone(prName+'_PDFDown')
  unc      = [0]*nbins
  alphaunc = [0]*nbins
  for var in pdfvars:
    for i in range(0, nbins):
      n = nom.GetBinContent(i)
      v = var.GetBinContent(i)
      unc[i] += (n-v)*(n-v)
  unc = [sqrt(x) for x in unc]

  if len(alphasvar) == 2:
    for i in range(0, nbins):
      vu = alphasvar[0].GetBinContent(i)
      vd = alphasvar[1].GetBinContent(i)
      alphaunc[i] = (vu-vd)/2
    unc = [sqrt(x*x+y*y) for x,y in zip(unc, alphaunc)]
  
  for i in range(0, nbins):
    n = nom.GetBinContent(i)
    up.SetBinContent(i, n+unc[i])
    do.SetBinContent(i, n-unc[i])
  return [nom, up, do]

def GetMEuncHisto(orderedHistos, prName='tt'):
  '''
  [1] muF = 0.50, muR = 0.50 
  [2] muF = 0.50, muR = 1.00 
  [3] muF = 0.50, muR = 2.00 (unphysical)
  [4] muF = 1.00, muR = 0.50 
  [5] muF = 1.00, muR = 1.00 (nominal)
  [6] muF = 1.00, muR = 2.00 
  [7] muF = 2.00, muR = 0.50 (unphysical)
  [8] muF = 2.00, muR = 1.00 
  [9] muF = 2.00, muR = 2.00 
  '''
  nom = orderedHistos[4]
  nom.SetName(prName)
  nbins = nom.GetNbinsX()+1
  up = nom.Clone(prName+'_ScaleUp')
  do = nom.Clone(prName+'_ScaleDown')
  uncUp  = [0]*nbins
  uncDo  = [0]*nbins
  hvar = [orderedHistos[0], orderedHistos[1], orderedHistos[3], orderedHistos[5], orderedHistos[7], orderedHistos[8]]
  
  for i in range(0, nbins):
    n = nom.GetBinContent(i)
    vals  = [h.GetBinContent(i) for h in hvar]
    diffs = [n-v for v in vals]
    uncDo[i] = min(diffs+[0])
    uncUp[i] = max(diffs+[0])

  for i in range(0, nbins):
    n = nom.GetBinContent(i)
    up.SetBinContent(i, n+uncUp[i])
    do.SetBinContent(i, n+uncDo[i])
  return [nom, up, do]


import argparse
parser = argparse.ArgumentParser(description='To select masses and year')
parser.add_argument('--year',         default=2018   , help = 'Year')
parser.add_argument('--mStop',        default=275  , help = 'Stop mass')
parser.add_argument('--mLSP',         default=100  , help = 'Neutralino mass')
parser.add_argument('--BS',          action='store_true'  , help = 'Do BS region')
parser.add_argument('--SR',          action='store_true'  , help = 'Do signal region')
parser.add_argument('--region',       default='SR'  , help = 'Select the region')
parser.add_argument('--sendJobs','-j'   , action='store_true'  , help = 'Send jobs!')
 
#args = parser.parse_args()
args, unknown = parser.parse_known_args()

ms   = int(args.mStop)
ml   = int(args.mLSP)
year = int(args.year)
sendJobs = args.sendJobs
argprocess = ''

treeName="MiniTree"
nSlots = 1

# Set signal masses
region = args.region
if args.BS: region = 'BS'
if args.SR: region = 'SR'

# Set constants
outpath = '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/stop_v629Mar/Unc/%s_PDFunc/%i/mass%i_%i/'%(region, year, ms, ml)
os.system("mkdir -p %s"%outpath)
model = '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/TopPlots/DrawMiniTrees/NNtotal_model2.h5'
# Create the looper, set readOutput to true to read previous temporary rootfiles created for each sample
pathToFiles = '/nfs/fanae/user/juanr/test/PAFnanoAOD/PDFminitree/'#path[year]
l = looper(path=pathToFiles if region=='SR' else pathBS[year], nSlots=nSlots, treeName = 'MiniTree', options = 'merge', outpath = outpath+'tempfiles/', readOutput=True)#, sendJobs=sendJobs)

# Add processes
processes = ['tt']
if argprocess != '': processes = argprocess
l.AddSample('tt', processDic[year]['tt'])

# Systematic uncertainties
#syst = 'MuonEff, ElecEff, Trig, JESCor, JESUnCor, JER, MuonES, ElecES, Uncl, Btag, MisTag, PU, TopPt, FSR, ISR, UE, hdamp, mtop' # PDF, ME
#syst += ',ME0,ME1,ME2,ME3,ME4,ME5,ME6,ME7,ME8'

systlist = []#[x+y for x in syst.replace(' ','').split(',') for y in ['Up','Down']]

# Lines below to read the DNN values
l.AddHeader('from framework.mva import ModelPredict\n')
l.AddInit('      self.pd1 = ModelPredict("%s")\n'%model)
l.AddInit("      self.systematics = ['']\n")
l.AddSyst(systlist)
loopcode = '''
values = [%i,  %i, t.TDilep_Pt, t.TDeltaPhi, t.TDeltaEta, t.TLep0Pt, t.TLep0Eta, t.TLep1Pt, vmet, t.TLep1Eta, vmll, vmt2, vht]
prob1 = self.pd1.GetProb(values)
'''%(ms, ml)
l.AddLoopCode(loopcode)

selection = '''
 passNonprompt = (t.TStatus == 1 or  t.TStatus == 22)
 if not passNonprompt: return 
'''
l.AddSelection(selection)

# Define expresions, including varibles with syst variations
l.AddExpr('deltaphi', 'TDeltaPhi', 'abs(TDeltaPhi)/3.141592')
l.AddExpr('deltaeta', 'TDeltaEta', 'abs(TDeltaEta)')
l.AddExpr('exprW', ['TWeight'], 'TWeight')
l.AddExpr('vmet', ['TMET'], 'TMET')
l.AddExpr('vmt2', ['TMT2'], 'TMT2')
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
  l.AddCut('(TMET < 50 or TMT2 < 80)', ['TMET', 'TMT2'])
l.AddCut('TNJets >= 2', 'TNJets')
l.AddCut('TNBtags >= 1', 'TNBtags')

# Add histograms
cut = ''
nPDFweights = 33 if year != 2016 else 100; nMEweights = 9;
tags = ['PDF']*nPDFweights + ['ME']*nMEweights
for tag,i in zip(tags, range(nPDFweights)+range(nMEweights)):
  l.AddHisto('vpd',  'dnn_'+'%s%i'%(tag,i),  20, 0, 1,   weight = 'TWeight_%s%i'%(tag,i), cut = '')
  l.AddHisto('vpd',  'dnn_10bins_'+'%s%i'%(tag,i),  10, 0, 1,   weight = 'TWeight_%s%i'%(tag,i), cut = '')
  l.AddHisto('vpd',  'dnn_30bins_'+'%s%i'%(tag,i),  30, 0, 1,   weight = 'TWeight_%s%i'%(tag,i), cut = '')
  l.AddHisto('vpd',  'dnn_40bins_'+'%s%i'%(tag,i),  40, 0, 1,   weight = 'TWeight_%s%i'%(tag,i), cut = '')
  l.AddHisto('vpd',  'dnn_5bins_'+'%s%i'%(tag,i),  5, 0, 1,   weight = 'TWeight_%s%i'%(tag,i), cut = '')
  l.AddHisto('TMll', 'mll_'+'%s%i'%(tag,i), 30, 0, 300, weight = 'TWeight_%s%i'%(tag,i), cut = '')
  if region == 'SR':
    l.AddHisto('TMET', 'met_'+'%s%i'%(tag,i), 25, 50, 300, weight = 'TWeight_%s%i'%(tag,i), cut = '')
    l.AddHisto('TMET', 'met_5bins_'+'%s%i'%(tag,i), 5, 50, 300, weight = 'TWeight_%s%i'%(tag,i), cut = '')
    l.AddHisto('TMT2', 'mt2_'+'%s%i'%(tag,i), 8, 80, 160, weight = 'TWeight_%s%i'%(tag,i), cut = '')
  else:
    l.AddHisto('TMET', 'met_'+'%s%i'%(tag,i), 30, 0, 300, weight = 'TWeight_%s%i'%(tag,i), cut = '')
    l.AddHisto('TMT2', 'mt2_'+'%s%i'%(tag,i), 16, 0, 160, weight = 'TWeight_%s%i'%(tag,i), cut = 'vmt2 > 0')
  l.AddHisto('TDilep_Pt', 'dileppt_'+'%s%i'%(tag,i), 30, 0, 300, weight = 'TWeight_%s%i'%(tag,i), cut = '')
  l.AddHisto('TLep0Pt', 'lep0pt_'+'%s%i'%(tag,i), 20, 0, 200, weight = 'TWeight_%s%i'%(tag,i), cut = '')
  l.AddHisto('TLep1Pt', 'lep1pt_'+'%s%i'%(tag,i), 15, 0, 150, weight = 'TWeight_%s%i'%(tag,i), cut = '')
  l.AddHisto('TLep0Eta', 'lep0eta_'+'%s%i'%(tag,i), 30, -2.4, 2.4, weight = 'TWeight_%s%i'%(tag,i), cut = '')
  l.AddHisto('TLep1Eta', 'lep1eta_'+'%s%i'%(tag,i), 30, -2.4, 2.4, weight = 'TWeight_%s%i'%(tag,i), cut = '')
  l.AddHisto('deltaphi', 'deltaphi_'+'%s%i'%(tag,i), 30, 0, 1, weight = 'TWeight_%s%i'%(tag,i), cut = '')
  l.AddHisto('deltaeta', 'deltaeta_'+'%s%i'%(tag,i), 30, 0, 5, weight = 'TWeight_%s%i'%(tag,i), cut = '')
  l.AddHisto('TJet0Pt', 'jet0pt_'+'%s%i'%(tag,i), 30, 0, 450, weight = 'TWeight_%s%i'%(tag,i), cut = '')
  l.AddHisto('TJet1Pt', 'jet1pt_'+'%s%i'%(tag,i), 30, 0, 300, weight = 'TWeight_%s%i'%(tag,i), cut = '')
  l.AddHisto('TJet0Eta', 'jet0eta_'+'%s%i'%(tag,i), 30, -2.4, 2.4, weight = 'TWeight_%s%i'%(tag,i), cut = '')
  l.AddHisto('TJet1Eta', 'jet1eta_'+'%s%i'%(tag,i), 30, -2.4, 2.4, weight = 'TWeight_%s%i'%(tag,i), cut = '')
  l.AddHisto('THT', 'ht_'+'%s%i'%(tag,i), 40, 0, 800, weight = 'TWeight_%s%i'%(tag,i), cut = '')
  l.AddHisto('TNJets', 'njets_'+'%s%i'%(tag,i), 6, 1.5, 7.5, weight = 'TWeight_%s%i'%(tag,i), cut = '')
  l.AddHisto('TNBtags', 'nbtags_'+'%s%i'%(tag,i), 3, 0.5, 3.5, weight = 'TWeight_%s%i'%(tag,i), cut = '')
  
histos  = ['mt2',  'met',  'mll',  'dnn',  'dileppt',  'deltaphi',  'deltaeta',  'ht',  'lep0pt',  'lep1pt',  'lep0eta',  'lep1eta', 'njets', 'nbtags', 'jet0pt', 'jet1pt', 'jet0eta', 'jet1eta'] 
histos += ['dnn_5bins', 'dnn_10bins', 'dnn_30bins', 'dnn_40bins']

out = l.Run()

if sendJobs: exit()

t = TopHistoReader(outpath+'tempfiles/')
print "Creating outputs in %s ..."%outpath
for var in histos:
  PDFhistosNom = t.GetNamedHisto(var+'_PDF0', 'tt')
  PDFhistos = [t.GetNamedHisto(var+'_PDF%i'%i, 'tt') for i in range(1, nPDFweights-2 if year != 2016 else nPDFweights)]
  AlphaShistos = [t.GetNamedHisto(var+'_PDF%i'%(nPDFweights-2), 'tt'), t.GetNamedHisto(var+'_PDF%i'%(nPDFweights-1), 'tt')] if year != 2016 else []
  pdfNom, pdfUp, pdfDown = GetPDFuncHisto(PDFhistosNom, PDFhistos, AlphaShistos, prName = 'tt')

  fout = TFile.Open(outpath+'/PDF/'+var+'.root', 'RECREATE')
  pdfNom.Write(); pdfUp.Write(); pdfDown.Write();
  fout.Close()

  MEhistos = [t.GetNamedHisto(var+'_ME%i'%i) for i in range(nMEweights)]
  meNom, meUp, meDown = GetMEuncHisto(MEhistos)

  fout = TFile.Open(outpath+'/Scale/'+var+'.root', 'RECREATE')
  meNom.Write(); meUp.Write(); meDown.Write();
  fout.Close()


######################################################################
### Plotting

titdic = {
  'mt2' : 'm_{T2} (GeV)',
  'met' : 'MET (GeV)',
  'dnn' : 'DNN score',
  'mll' : 'm_{e#mu} (GeV)',
  'deltaeta' : '#Delta#eta(e#mu)',
  'deltaphi' : '#Delta#phi(e#mu) (rad/#pi)',
  'ht' : 'H_{T} (GeV)',
  'jet0pt' : 'Leading jet p_{T} (GeV)',
  'jet1pt' : 'Subeading jet p_{T} (GeV)',
  'lep0pt' : 'Leading lepton p_{T} (GeV)',
  'lep1pt' : 'Subleading lepton p_{T} (GeV)',
  'lep0eta': 'Leading lepton #eta',
  'lep1eta': 'Subleading lepton #eta',
  'jet0eta': 'Leading jet #eta',
  'jet1eta': 'Subleading jet #eta',
  'njets'  : 'Jet multiplicity',
  'nbtags' : 'b tag multiplicity',
  'dileppt': 'p_{T}(e#mu) (GeV)',
}


out = '/nfs/fanae/user/juanr/www/stopLegacy/nanoAODv6/29mar/%i/'%year
def SavePlots(s, var = 'mt2', sampName = 'tt', tag = 'PDF uncertainty'):
  tr = TopHistoReader(outpath+s)
  a = HistoUnc(out+'/PDF%s/'%sampName, var+sampName+s, tag=tag, xtit = titdic[var] if var in titdic.keys() else '')
  a.SetLumi(GetLumi(year))
  a.AddHistoNom( tr.GetNamedHisto(sampName, var))
  a.AddHistoUp(  tr.GetNamedHisto(sampName+'_'+s+'Up', var))
  a.AddHistoDown(tr.GetNamedHisto(sampName+'_'+s+'Down', var))
  a.Draw()

for var in titdic.keys():
  SavePlots('PDF',   var=var, tag='PDF uncertainty')
  SavePlots('Scale', var=var, tag='#mu_{R} and #mu_{F} scales uncertainty')


