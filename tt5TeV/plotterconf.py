import os, sys
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)
from framework.functions import GetLumi
from plotter.TopHistoReader import TopHistoReader, HistoManager
from plotter.Plotter import Stack
from ROOT.TMath import Sqrt as sqrt
from ROOT import kRed, kOrange, kBlue, kTeal, kGreen, kGray, kAzure, kPink, kCyan, kBlack, kSpring, kViolet, kYellow

### Input and output
path = '../temp5TeV/testinvmass/'
outpath = './outputs_testinvmass/'

### Definition of the processes
processDic = {
'VV'  : 'WZTo3LNU,WWTo2L2Nu',
'fake': 'WJetsToLNu,TTsemilep',
'tW'  : 'tW_noFullHad,  tbarW_noFullHad',
'DY'  : 'DYJetsToLL_M_10to50,DYJetsToLL_MLL50',
'tt'  : 'TT',
'data': 'HighEGJet,SingleMuon, DoubleMuon'}
processes = ['VV', 'fake', 'DY', 'tt', 'tW']

### Definition of colors for the processes
colors ={
'VV'  : kTeal+5,
'fake': kGray+2,
'tW'  : kOrange+1,
'DY'  : kAzure+2,
'tt'  : kRed+1,
'data': 1}

systematics = 'MuonEff, ElecEff'

Lumi = 296.1

def GetName(var, chan, lev):
  return var + '_' + chan + '_' + lev
