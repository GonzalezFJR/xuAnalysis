import os,sys
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)
from framework.analysis import analysis
import framework.functions as fun
from ROOT import TLorentzVector, gSystem, gROOT
from array import array

# Load mt2
pathtolib = "%s/src/BTagSFUtil/"%basepath
if os.path.isfile(pathtolib + 'BTagSFUtil_cc.so'):
  gSystem.Load(pathtolib+ 'BTagSFUtil_cc.so')
else:
  gROOT.LoadMacro(pathtolib+ 'BTagSFUtil.C+')
from ROOT import BTagSFUtil,TString

class BtagReader:

  def __init__(self, taggerName = "DeepFlav", meastype = "mujets", wp = "Medium", year = 2017):
    taggerName=TString(taggerName); #"DeepFlav","CSVv2";"DeepCSV";
    MeasType = TString(meastype); # comb, mujets
    stringWP = TString(wp);
    self.fBTagSFnom = BTagSFUtil(MeasType.Data(), pathtolib, taggerName.Data(), stringWP,  0, year, '');
    self.fBTagSFbUp = BTagSFUtil(MeasType.Data(), pathtolib, taggerName.Data(), stringWP,  1, year, '');
    self.fBTagSFbDo = BTagSFUtil(MeasType.Data(), pathtolib, taggerName.Data(), stringWP, -1, year, '');
    self.fBTagSFlUp = BTagSFUtil(MeasType.Data(), pathtolib, taggerName.Data(), stringWP,  3, year, '');
    self.fBTagSFlDo = BTagSFUtil(MeasType.Data(), pathtolib, taggerName.Data(), stringWP, -3, year, '');

  def IsBtag(self, alg, flav, pt, eta, syst = 0):
    if   syst ==  1: return self.fBTagSFbUp.IsTagged(alg, flav, pt, eta)
    elif syst == -1: return self.fBTagSFbDo.IsTagged(alg, flav, pt, eta)
    elif syst ==  3: return self.fBTagSFlUp.IsTagged(alg, flav, pt, eta)
    elif syst == -3: return self.fBTagSFlDo.IsTagged(alg, flav, pt, eta)
    else           : return self.fBTagSFnom.IsTagged(alg, flav, pt, eta)
