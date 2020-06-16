import os, sys
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)
from plotter.TopHistoReader import TopHistoReader, HistoManager
from plotter.Plotter import Stack, HistoComp
from framework.looper import looper
from ROOT.TMath import Sqrt as sqrt
from ROOT import kRed, kOrange, kBlue, kTeal, kGreen, kGray, kAzure, kPink, kCyan, kBlack, kSpring, kViolet, kYellow
from ROOT import TCanvas, gROOT, TLegend, TCanvas, TFile
gROOT.SetBatch(1)
from stop.config import *

GetPath    = lambda year, ms, ml : '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/16apr/LEE/Unc/SR/%s/mass%s_%s/tempfiles/'%(str(year), str(ms), str(ml))
GetPathNom = lambda year, ms, ml : '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/16apr/Unc/SR/%s/mass%s_%s/tempfiles/'%(str(year), str(ms), str(ml))
GetHisto = lambda itoy : 'dnn_NormToy%s'%str(itoy) if itoy >=0 else 'dnn'
hname = lambda ms, ml, itoy : ('pseudodata_%s_%s_toy%s'%(str(ms), str(ml), str(itoy))) if itoy >= 0 else 'pseudodata_%s_%s'%(str(ms), str(ml))
nToys = 100

year = 2018
outpath = 'histos/'
outname = 'LEEpseudodata%s.root'%str(year)
webpath = webpath+'/LEE/conditioning/'
if not os.path.isdir(webpath): os.system('mkdir -p %s'%webpath)

import ROOT
import copy
from numpy import ceil, mean
from scipy.stats import chi2 as chi2

ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(True)
masses = GetAllStopNeutralinoPoints(mode='diag')
inFNorm = TFile.Open(outpath+outname)

#inFNaive = ROOT.TFile.Open("allBootstraps/2016_dataobs_bootstrap_naive.root","READ")
pullsNorm  = ROOT.TH1F("pulls_norm", "pulls_norm", 51,-0.0005,0.0505)


def produceVals(inF,toy,histType):
  inC = {}
  inH = {}
  yields = []
  for ms, ml in masses:
    inH['%i_%i'%(ms, ml)] = inF.Get(hname(ms, ml, toy))
    yields.append(inH['%i_%i'%(ms,ml)].Integral())
  central = mean(yields)
  minY = -0.0525
  maxY = 0.0525
  nbins = 21
  condHisto = ROOT.TH1F("cond_%s_%i"%(histType, toy),"cond_%s_%i"%(histType, toy),nbins, minY, maxY)
  maxdev = 0
  for y in yields:
    val = (y-central)/central
    if abs(val) > maxdev: maxdev = abs(val)
    condHisto.Fill(val)
  if histType == "Norm":
    pullsNorm.Fill(maxdev)

  return condHisto

for toy in range(0,nToys):
  print "Toy:", toy
  c = ROOT.TCanvas("c","c",800,600)
  condNorm = produceVals(inFNorm, toy, "Norm")
  
  condNorm.SetLineColor(ROOT.kBlue)
  tl = ROOT.TLegend(0.6,0.7,0.9,0.9)
  tl.AddEntry(condNorm, "Standard, yield pull","l")

  condNorm.SetTitle("")
  condNorm.GetXaxis().SetTitle("Yields pull")
  condNorm.GetYaxis().SetTitle("# Mass hypothesis")

  condNorm.Draw("hist")
  tl.Draw("same")
  for f in ['pdf', 'png']: c.SaveAs(webpath+'condscomp_all_%i.%s'%(toy,f))

c = ROOT.TCanvas("c","c",800,600)
pullsNorm.SetLineColor(ROOT.kBlue)
tl = ROOT.TLegend(0.6,0.7,0.9,0.9)
tl.AddEntry(pullsNorm, "Standard, max deviations","l")
pullsNorm.SetTitle("")
pullsNorm.GetXaxis().SetTitle("Max yields pull deviation")
pullsNorm.GetYaxis().SetTitle("Toys")
pullsNorm.Draw("hist")
tl.Draw("same")
for f in ['pdf', 'png']: c.SaveAs(webpath+'maxdevcomp_all.%s'%(f))
