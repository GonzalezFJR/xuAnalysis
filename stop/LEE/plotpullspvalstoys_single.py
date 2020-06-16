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

#GetPath    = lambda year, ms, ml : '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/16apr/LEE/Unc/SR/%s/mass%s_%s/tempfiles/'%(str(year), str(ms), str(ml))
#GetPathNom = lambda year, ms, ml : '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/16apr/Unc/SR/%s/mass%s_%s/tempfiles/'%(str(year), str(ms), str(ml))
#GetHisto = lambda itoy : 'dnn_NormToy%s'%str(itoy) if itoy >=0 else 'dnn'
hname = lambda ms, ml, itoy : ('pseudodata_%s_%s_toy%s'%(str(ms), str(ml), str(itoy))) if itoy >= 0 else 'pseudodata_%s_%s'%(str(ms), str(ml))
nToys = 100

year = 2018
outpath = 'histos/'
outname = 'LEEpseudodata%s.root'%str(year)
webpath = webpath+'/LEE/pulls/'
if not os.path.isdir(webpath): os.system('mkdir -p %s'%webpath)

import ROOT
import copy
from numpy import ceil
from scipy.stats import chi2 as chi2
ROOT.gStyle.SetOptStat(0)

inFNorm = TFile.Open(outpath+outname)
masses = GetAllStopNeutralinoPoints(mode='diag')

pullsNorm = ROOT.TH1F("pulls_norm", "pulls_norm", 50,-1,1)
pvalsNorm = ROOT.TH1F("pvals_norm", "pvals_norm", 25,0,1)

def produceVals(inF, ms, ml):
  values = []
  central = []
  thePois = []
  num = []
  inC = inF.Get(hname(ms, ml, -1))
  nbins = inC.GetNbinsX()
  for b in range(1,nbins): 
    print 'content = ', inC.GetBinContent(b)
    central.append(inC.GetBinContent(b))
    hLow = max(0,round(central[-1] - 4*(central[-1])**0.5))
    hHigh = round(central[-1] + 4*(central[-1])**0.5)
    nBins = min(40,ceil(hHigh-hLow))
    binWidth = ceil((hHigh-hLow)/nBins)
    hLow = hLow - binWidth/2.
    hHigh = hLow + (nBins+1)*binWidth
    nBins += 1
    nBins = int(nBins)
    values.append(ROOT.TH1F("h"+str(b) + inF.GetName(),"h"+str(b)+ inF.GetName(), nBins, hLow, hHigh))
    thePois.append( ROOT.TF1("fit"+str(b)+ inF.GetName(),"%1.3f*TMath::Poisson(x,[0])"%((hHigh-hLow)/nBins),hLow, hHigh))
    thePois[-1].SetParameter(0, central[-1])
    num.append(0)

  for w in range(0,nToys):
    inH = inF.Get(hname(ms, ml, w))
    for b in range(1,nbins):
      values[b-1].Fill(inH.GetBinContent(b))#-central[b-1])
      num[b-1] += 1 
    values[b-1].Sumw2()
 
  for b in range(1,nbins):
    values[b-1].Scale(1./num[b-1])
    #print values[b-1].Integral()
  return values, thePois, central
  

def produceHistos(ms, ml):
  valuesNorm, thePoisNorm, centralNorm = produceVals(inFNorm, ms, ml)
 
  c = ROOT.TCanvas("c","c",800,600)
  for i in range(len(valuesNorm)):
    thePoisCentral = thePoisNorm[i].Clone("theCentralPoisson")
    valuesNorm[i].Fit(thePoisNorm[i],"L")
    valuesNorm[i].SetLineColor(ROOT.kBlue)
    valuesNorm[i].GetXaxis().SetTitle("Yields in bin %i ms=%i, ml=%i"%(i,ms,ml))
    valuesNorm[i].GetYaxis().SetTitle("Toys/(Total)")
    valuesNorm[i].SetTitle("Toy distribution of yields in bin %i ms=%i, ml=%i"%(i,ms,ml))
    valuesNorm[i].Draw("hist")
    thePoisNorm[i].SetLineColor(ROOT.kBlue)
    thePoisNorm[i].Draw("same")
    thePoisCentral.SetLineColor(ROOT.kBlack)
    thePoisCentral.Draw("same")

    tl = ROOT.TLegend(0.6,0.7,0.9,0.9)
    tl.AddEntry(thePoisNorm[i] , "Norm (fit,pval): %1.3f, %1.5f"%(thePoisNorm[i].GetParameter(0), thePoisNorm[i].GetProb()),"l")

    tl.AddEntry(thePoisCentral, "Expected pois (exp): %1.3f"%centralNorm[i], "l")
    tl.Draw("same")

    for f in ['pdf', 'png']: c.SaveAs(webpath+'check_%i_%i_bin%i.%s'%(ms,ml,i,f))

    pullsNorm.Fill((thePoisNorm[i].GetParameter(0) - centralNorm[i])/(thePoisNorm[i].GetParError(0)))
    pvalsNorm.Fill(thePoisNorm[i].GetProb())


for ms, ml in masses:
  print "=================================================="
  print "=================================================="
  print "Processing ms=%i, ml=%i"%(ms, ml)
  produceHistos(ms, ml)
  print "=================================================="
  print "=================================================="

c = ROOT.TCanvas("c","c",800,600)

pullsNorm.SetTitle("Toys vs pulls of fitted #nu value")
pullsNorm.SetLineColor(ROOT.kBlue)
tl = ROOT.TLegend(0.6,0.7,0.9,0.9)
tl.AddEntry(pullsNorm, "Norm, pulls","l")
pullsNorm.GetXaxis().SetTitle("(#nu_{fit}-#nu_{exp})/#epsilon(#nu_{fit})")
pullsNorm.GetYaxis().SetTitle("Toys/(Total)")
pullsNorm.Draw("hist")
tl.Draw("same")
for f in ['pdf', 'png']: c.SaveAs(webpath+'pulls_all.%s'%f)

pvalsNorm.SetTitle("Toys vs p-values of fit to a Poissonian")
pvalsNorm.SetLineColor(ROOT.kBlue)
tl = ROOT.TLegend(0.6,0.7,0.9,0.9)
tl.AddEntry(pvalsNorm, "Norm, pvals","l")
pvalsNorm.GetXaxis().SetTitle("Toy fit to poissonian p-value")
pvalsNorm.GetYaxis().SetTitle("Toys/(Total)")

pvalsNorm.Draw("hist")
tl.Draw("same")
for f in ['pdf', 'png']: c.SaveAs(webpath+'pvals_all.%s'%f)


