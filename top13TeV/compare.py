import os, sys
from conf import *
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)
from plotter.TopHistoReader import TopHistoReader, HistoManager
from plotter.Plotter import Stack, HistoComp
from ROOT.TMath import Sqrt as sqrt
from ROOT import kRed, kOrange, kBlue, kTeal, kGreen, kGray, kAzure, kPink, kCyan, kBlack, kSpring, kViolet, kYellow
from ROOT import TCanvas, gROOT
gROOT.SetBatch(1)

tr1 = TopHistoReader(path=path[2016])
tr2 = TopHistoReader(path=path[2018])#'/pool/ciencias/userstorage/juanr/top/2016/nov15/') # TOP-17-001

s = HistoComp(outpath = './temp/', doNorm = True, doRatio = True)
s.autoRatio = True
s.SetTextLumi('Normalized distributions', texlumiX = 0.12)

hname = 'H_NJets_ElMu_dilepton'
s.AddHisto(tr1.GetNamedHisto(hname, 'TT'), 'hist', 'hist', '2016', color = kAzure+2)
s.AddHisto(tr2.GetNamedHisto(hname, 'TTTo2L2Nu'), 'hist', 'hist', '2018', color = kRed+1)
s.SetXtitle('Jet multiplicity')
s.SetOutName('temp')
s.Draw()

