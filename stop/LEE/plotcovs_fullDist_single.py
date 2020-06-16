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
webpath = webpath+'/LEE/covs/'
if not os.path.isdir(webpath): os.system('mkdir -p %s'%webpath)

import ROOT
import copy
from numpy import ceil
from scipy.stats import chi2 as chi2
ROOT.gStyle.SetOptStat(0)

import ROOT
import copy
from numpy import ceil
import numpy as np
from scipy.stats import chi2 as chi2
from multiprocessing import Pool
from contextlib import closing
import time

ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPaintTextFormat("1.3f")
ROOT.gROOT.SetBatch(True)

inFNorm = TFile.Open(outpath+outname)
masses = GetAllStopNeutralinoPoints(mode='diag')
nbins = 20

def produceVals(coms):
  inF = coms[0]
  ms1, ml1 = coms[1]
  ms2, ml2 = coms[2]
  typ = coms[3]
  vals1 = {}
  vals2 = {}
  covars = ROOT.TH2D("hist%s_m1%i_%i_m2_%i_%i"%(typ,ms1,ml1,ms2,ml2),"hist%s_m1%i_%i_m2_%i_%i"%(typ,ms1,ml1,ms2,ml2),nbins,0.5,nbins+0.5,nbins,0.5,nbins+0.5)
  print "Getting yields..."
  inC1 = inF.Get(hname(ms1, ml1, -1))
  inC2 = inF.Get(hname(ms2, ml2, -1))
  for w in range(0,nToys):
    inH1 = inF.Get(hname(ms1, ml1, w))
    inH2 = inF.Get(hname(ms2, ml2, w))
    for b1 in range(1,nbins+1):
      for b2 in range(1,nbins+1):
        pull1 = (inH1.GetBinContent(b1)-inC1.GetBinContent(b1))#/(inC1.GetBinContent(b1))**0.5
        pull2 = (inH2.GetBinContent(b2)-inC2.GetBinContent(b2))#/(inC2.GetBinContent(b2))**0.5
        if not (b1,b2) in vals1.keys():
          vals1[(b1,b2)] = [pull1]
          vals2[(b1,b2)] = [pull2]
        else:
          vals1[(b1,b2)].append(pull1)
          vals2[(b1,b2)].append(pull2)
  print "Filling covariance...."
  for b1 in range(1,nbins+1):
    print "....step %i of %i"%(b1-1, nbins)
    for b2 in range(1,nbins+1):
      vec1 = np.array(vals1[(b1,b2)])
      vec2 = np.array(vals2[(b1,b2)])
      covars.SetBinContent(b1,b2, np.cov(vec1,vec2)[0,1]/(np.var(vec1)*np.var(vec2))**0.5)

  
  c = ROOT.TCanvas("c","c",1200,800)
  covars.SetTitle("Correlation between bins in the [%i, %i] and [%i, %i] discriminants"%(ms1, ml1, ms2, ml2))
  covars.GetZaxis().SetRangeUser(-1,1)
  covars.GetXaxis().SetTitle("Bins in [%i, %i]"%(ms1, ml1))
  covars.GetYaxis().SetTitle("Bins in [%i, %i]"%(ms2, ml2))
  covars.Draw("textcolz")
  for f in ['pdf', 'png']: c.SaveAs(webpath+'covs%s_m%i_%i_m%i_%i.%s'%(typ,ms1,ml1,ms2,ml2,f))


for ms1, ml1 in masses:
  for ms2, ml2 in masses:
    produceVals([inFNorm, [ms1, ml1], [ms2, ml2], "Norm"])

"""with closing(Pool(4)) as p:
        print "Now running " + str(len(commands)) + " commands using: " + str(10) + " processes. Please wait"
        retlist1 = p.map_async(produceVals, commands, 1)
        while not retlist1.ready():
                print("Combine runs left: {}".format(retlist1._number_left ))
                time.sleep(1)
        retlist1 = retlist1.get()
        p.close()
        p.join()
        p.terminate()"""
