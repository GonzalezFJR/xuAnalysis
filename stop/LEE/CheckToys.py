import os, sys
from config import *
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)
from plotter.TopHistoReader import TopHistoReader, HistoManager
from plotter.Plotter import Stack, HistoComp
from framework.looper import looper
from ROOT.TMath import Sqrt as sqrt
from ROOT import kRed, kOrange, kBlue, kTeal, kGreen, kGray, kAzure, kPink, kCyan, kBlack, kSpring, kViolet, kYellow
from ROOT import TCanvas, gROOT, TLegend, TCanvas, TFile, TH1F, TLine
from numpy import arange
gROOT.SetBatch(1)
import argparse

year = 2018
ms = 275
ml = 100
nToys = 100
baseoutpath +='/LEE/Unc/SR/%i/mass%i_%i/tempfiles/'
webpath     +='/LEE/'

def CheckToysTempFiles(sample='tW', histo='dnn'):
  path = baseoutpath%(year, ms, ml)
  f = TFile.Open(path+sample+ ('.root' if not sample.endswith('.root') else ''))
  hnom = f.Get(histo)
  nom = hnom.Integral()
  h = TH1F('h', 'h', 20, 0.24, 0.26)
  for i in range(nToys):
    ht = f.Get(histo+'_NormToy%i'%i)
    h.Fill(ht.Integral())

  c = TCanvas('c', 'c', 10, 10, 1200, 800)
  h.SetStats(0)
  h.SetTitle('')
  h.GetXaxis().SetTitle("Yield %s"%sample)
  h.GetYaxis().SetTitle("Number of toys")
  h.SetLineWidth(2); h.SetLineColor(kOrange+1)
  h.SetFillColor(0)
  h.Draw('hist')

  l = TLine(nom, 0, nom, h.GetMaximum())
  l.SetLineColor(kGray+3); l.SetLineWidth(2); l.SetLineStyle(2)
  l.Draw("same")

  name = 'toys_%s_%s'%(sample, histo)
  for form in ['png', 'pdf']: c.SaveAs(webpath+name+'.'+form)

CheckToysTempFiles(sample='tt', histo='dnn')
