import os, sys
from conf import *
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)
from plotter.TopHistoReader import TopHistoReader, HistoManager
from plotter.Plotter import HistoComp
from ROOT.TMath import Sqrt as sqrt
from ROOT import kRed, kOrange, kBlue, kTeal, kGreen, kGray, kAzure, kPink, kCyan, kBlack, kSpring, kViolet, kYellow
from ROOT import TCanvas, gROOT
gROOT.SetBatch(1)

systdic = {
 't#bar{t}': {
   'hdampUp'   : 'TTTo2L2Nu_hdampUp',
   'hdampDown' : 'TTTo2L2Nu_hdampDown',
   'TuneUp'    : 'TTTo2L2Nu_TuneCP5Up',
   'TuneDown'  : 'TTTo2L2Nu_TuneCP5Down'
   }
}
path = '/nfs/fanae/user/andreatf/PAFnanoAOD/temp2018_new/'
systematics = 'MuonEff, ElecEff, PU, Btag, Mistag, hdamp, Tune'
hm = HistoManager(['t#bar{t}'], systematics, '', path = path, processDic=processDic[2018], lumi = GetLumi(2018)*1000, systdic = systdic)

def DrawHisto(hname = 'H_NJets_ElMu_1btag', syst = 'ElecEff', systname = 'Electron Efficiency', out = 'temp', xtit = 'Jet Multiplicity'):
  hm.SetHisto(hname, rebin = 100)
  histo    = hm.GetUncHist(syst, includeStat = True).Clone("nom")
  histoUnc = histo.Clone("syst")
  histo.SetFillStyle(0)
  histoUnc.SetFillStyle(1000)
  histoUnc.SetFillColorAlpha(kAzure+2, 0.5)
  histoUnc.SetLineWidth(0)
  hratio = hm.GetRatioHistoUnc(syst, includeStat = True)

  s = HistoComp(outpath = './temp/', doNorm = False, doRatio = True)
  s.SetLumi(GetLumi(2018))
  s.AddHisto(     histo,  'hist', '', 't#bar{t}')
  s.AddHisto(  histoUnc,  '', 'e2', systname)
  s.AddRatioHisto(hratio, 'e2')
  s.SetOutName(out)
  s.SetLegendPos(ncol = 1)
  s.SetRatioMax(1.1)
  s.SetRatioMin(0.9)
  s.SetYratioTitle("Uncertainty")
  s.SetXtitle(xtit)
  s.Draw()

DrawHisto('H_MT2_ElMu_1btag', 'ElecEff', 'Electron efficiency', 'temp', xtit = 'm_{T2} (GeV)')
