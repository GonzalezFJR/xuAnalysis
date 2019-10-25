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
path = '/mnt_pool/ciencias_users/user/juanr/dev/xuAnalysis/temp5TeV/oct22/'
outpath = './WW5TeVplots/'

### Definition of the processes
processDic = {
'VZ'  : 'WZTo3LNU,ZZTo2L2Nu,ZZTo4L',
'WW'  : 'WWTo2L2Nu',
'Nonprompt': 'WJetsToLNu,TTsemilep',
'top'  : 'TT,tW_noFullHad,  tbarW_noFullHad',
'DY'  : 'DYJetsToLL_M_10to50,DYJetsToLL_MLL50',
'data': 'HighEGJet, SingleMuon'}##SingleMuon
processes = ['VZ', 'Nonprompt', 'DY', 'top', 'WW']

### Definition of colors for the processes
colors ={
'WW'  : kTeal+5,
'Nonprompt': kGray+2,
'VZ'  : kOrange+1,
'DY'  : kAzure+2,
'top' : kRed+1,
'data': 1}

systematics = 'MuonEff, ElecEff, TrigEff, JES, JER'#, Prefire, ISR, FSR'

Lumi = 296.1 #294.24 #296.1

def GetName(var, chan, lev):
  return (var + '_' + chan + '_' + lev) if lev != '' else (var + '_' + chan)
