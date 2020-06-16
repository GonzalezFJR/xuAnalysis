import os,sys
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import numpy as np

class ElectronScaleSmear:
  def __init__(self,fileName,doSys=True):
    self.fileName = fileName
    self.doSys = doSys

    pathtolib = "%s/src/EnergyScaleCorrection_cc.so"%basepath
    if os.path.isfile(pathtolib): 
      ROOT.gSystem.Load(pathtolib)
    else:
      ROOT.gROOT.ProcessLine(".L %s/src/EnergyScaleCorrection.cc++" %basepath)
    dummy = ROOT.EnergyScaleCorrection
    self.eleCorr = ROOT.EnergyScaleCorrection(self.fileName, ROOT.EnergyScaleCorrection.ECALELF)
    self.eCorr = 1

  def SetPrevCor(self, cor):
    self.eCorr = cor

  def GetScaleCorr(self, run, pt, eta, phi, m, r9, seedGain=12):
    e = ROOT.TLorentzVector()
    e.SetPtEtaPhiM(pt, eta, phi, m)
    praw = e*(1./self.eCorr) # Correct back
    et = praw.Et()
    abseta = abs(praw.Eta())
    escale = self.eleCorr.scaleCorr(run, et, abseta, r9)
    vEle = praw*escale
    return vEle.Pt(), vEle.M()

  def GetSmearCorr(self, run, pt, eta, phi, m, r9, seedGain=12):
    e = ROOT.TLorentzVector()
    e.SetPtEtaPhiM(pt, eta, phi, m)
    praw = e*(1./self.eCorr) # Correct back
    et = praw.Et()
    abseta = abs(praw.Eta())
    eleSmear = self.eleCorr.smearingSigma(run, et, abseta, r9, 12, 0, 0.)
    nrandom = ROOT.gRandom.Gaus(0,1)
    vEle = praw*(1+eleSmear*nrandom)
    if self.doSys:
      escaleErr   = self.eleCorr.scaleCorrUncert(run, et, abseta, r9)
      eleSmearUp  = self.eleCorr.smearingSigma(run, et, abseta, r9, 12,  1, 0.)
      eleSmearDo  = self.eleCorr.smearingSigma(run, et, abseta, r9, 12, -1, 0.)
      eleSmearUnc = nrandom*np.sqrt( (eleSmearUp-eleSmear)*(eleSmearUp-eleSmear) + (eleSmearDo-eleSmear)*(eleSmearDo-eleSmear) )
      vEleUp = vEle*(1+escaleErr+eleSmearUnc)
      vEleDo = vEle*(1-escaleErr-eleSmearUnc)
      return (vEle.Pt(), vEleUp.Pt(), vEleDo.Pt(), vEle.M(), vEleUp.M(), vEleDo.M())
    else: return vEle.Pt(), vEle.M()

  def GetUnc(self, run, pt, eta, phi, m, r9, seedGain=12):
    e = ROOT.TLorentzVector()
    e.SetPtEtaPhiM(pt, eta, phi, m)
    et = e.Et()
    abseta = abs(e.Eta())
    nrandom = ROOT.gRandom.Gaus(0,1)
    eleSmear = self.eleCorr.smearingSigma(run, et, abseta, r9, 12, 0, 0.)
    eleSmearUp  = self.eleCorr.smearingSigma(run, et, abseta, r9, 12,  1, 0.)
    eleSmearDo  = self.eleCorr.smearingSigma(run, et, abseta, r9, 12, -1, 0.)
    escaleErr   = self.eleCorr.scaleCorrUncert(run, et, abseta, r9)
    eleSmearUnc = nrandom*np.sqrt( (eleSmearUp-eleSmear)*(eleSmearUp-eleSmear) + (eleSmearDo-eleSmear)*(eleSmearDo-eleSmear) )
    vEleUp = e*(1+escaleErr+eleSmearUnc)
    vEleDo = e*(1-escaleErr-eleSmearUnc)
    return (vEleUp.Pt(), vEleDo.Pt(), vEleUp.M(), vEleDo.M())

# python SubmitDatasets.py --dataset /SingleElectron/Run2017B-Nano25Oct2019-v1/NANOAOD --options data --test -y 17 --prodName testElecESdata2017_28apr

pufile_mc2016="%s/inputs/pileup/pileup_profile_Summer16.root" %basepath
fname2016="%s/inputs/elecES/Legacy2016_07Aug2017_FineEtaR9_v3_ele_unc" % basepath
fname2017="%s/inputs/elecES/Run2017_17Nov2017_v1_ele_unc" % basepath
fname2018="%s/inputs/elecES/Run2018_Step2Closure_CoarseEtaR9Gain_v2" % basepath
fname2017LowPU="%s/inputs/elecES/Run2017_LowPU_v2" % basepath

elecUnc2016 = lambda : ElectronScaleSmear(fname2016)
elecUnc2017 = lambda : ElectronScaleSmear(fname2017)
elecUnc2018 = lambda : ElectronScaleSmear(fname2018)

elecScale5TeV         = lambda : ElectronScaleSmear(fname2017LowPU,doSys=False) # run=306936
elecScale2017LowPu    = lambda : ElectronScaleSmear(fname2017LowPU)

