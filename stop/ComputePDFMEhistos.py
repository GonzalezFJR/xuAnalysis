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

doStack = False
doPlotSyst = True
year = 2018#'comb'#2016
ms = 275
ml = 100
region = 'SR' #'ttmt2'
process = 'tt'#, tW, ttZ, Others'
GetPath = lambda region, year, ms, ml : '../stop_v629Mar/Unc/%s_PDFunc/%s/mass%i_%i/'%(region, str(year), ms, ml) # v611Feb NewSyst
GetOutpath = lambda region, year, ms, ml : '/nfs/fanae/user/juanr/www/stopLegacy/nanoAODv6/29mar/PDFunc/mass%i_%i/%s/%s/'%(ms, ml, region,str(year))
path    = GetPath(region,year, ms, ml)
outpath = GetOutpath(region,year, ms, ml)

sysdic = {
'PDF' : 'PDF',
'ME' : '#mu_{R} and #mu_{F} scales',
}

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

nPDF = 33
var = 'met'
syst = ['PDF%i'%i for i in range(nPDF)]
hm = HistoManager(process, syst, path=path)
hm.ReadHistosFromFile(var)
