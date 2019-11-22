import os, sys
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)
from framework.functions import GetLumi
from plotter.TopHistoReader import TopHistoReader, HistoManager
from plotter.Plotter import Stack
from ROOT.TMath import Sqrt as sqrt
from ROOT import kRed, kOrange, kBlue, kTeal, kGreen, kGray, kAzure, kPink, kCyan, kBlack, kSpring, kViolet, kYellow

### Input and output
#path = '../temp5TeV/sep17/'
#path = '/mnt_pool/ciencias_users/user/juanr/dev/xuAnalysis/temp5TeV/sep22/'
path = '/mnt_pool/ciencias_users/user/juanr/dev/xuAnalysis/temp5TeV/nov21v2/'
outpath = '/nfs/fanae/user/juanr/www/tt5TeV/metCheck/'

### Definition of the processes
processDic = {
'VV'  : 'WZTo3LNU,WWTo2L2Nu,ZZTo2L2Nu,ZZTo4L',
'Nonprompt': 'TTsemilep, W0JetsToLNu,W1JetsToLNu,W2JetsToLNu,W3JetsToLNu',#'WJetsToLNu,TTsemilep',
'tW'  : 'tW_noFullHad,  tbarW_noFullHad',
#'DY'  : 'DYJetsToLL_MLL50',
'DY'  : 'DYJetsToLL_M_10to50,DYJetsToLL_MLL50',
'tt'  : 'TT',
'data': 'HighEGJet, SingleMuon'}##SingleMuon
processes = ['VV', 'Nonprompt', 'DY', 'tW', 'tt']

### Definition of colors for the processes
colors ={
'VV'  : kTeal+5,
'Nonprompt': kGray+2,
'tW'  : kOrange+1,
'DY'  : kAzure+2,
'tt'  : kRed+1,
'data': 1}

systematics = 'MuonEff, ElecEff, TrigEff, JES, JER'#, Prefire, ISR, FSR'

Lumi = 296.1 #294.24 #296.1

def GetName(var, chan, lev):
  return (var + '_' + chan + '_' + lev) if lev != '' else (var + '_' + chan)
