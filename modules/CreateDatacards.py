# python ../../../modules/CreateDatacards.py mt2 -s stop275_100 -u "MuonEff, ElecEff, Trig, PU, ISR, FSR, Pref"
import os,sys
from ROOT import gROOT
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)

# Load Datacard.C
pathtolib = "%s/src/"%basepath
if os.path.isfile(pathtolib + 'Datacard_cc.so'):
  gSystem.Load(pathtolib+ 'Datacard_cc.so')
else:
  gROOT.LoadMacro(pathtolib+ 'Datacard.C+')
from ROOT import Datacard

def CreateDatacard(signal, path, var, allBkg, NormSyst, LumiSys, syst = "MuonEff", chan = 'ElMu'):
  d = Datacard(signal, allBkg, syst, chan);
  d.SetPathToFile(path)
  d.SetRootFileName(var)
  d.GetParamsFormFile()
  d.SetNormUnc(NormSyst);
  d.SetLumiUnc(1+LumiSys)
  d.doBeestonBarlow = True
  d.PrintDatacard(path + "/datacard_" + var + "_" + signal + "_" + chan + ".txt")
  return d

import argparse
parser = argparse.ArgumentParser(description='Create datacards')
parser.add_argument('filename'          , default=''           , help = 'Name of the file')
parser.add_argument('--path', '-p'      , default='./'         , help = 'Path to look rootfile')
parser.add_argument('--verbose','-v'    , default=0            , help = 'Activate the verbosing')
parser.add_argument('--bkg','-b'        , default='ttZ,  Nonprompt, Other, tW, tt'     , help = 'Background processes')
parser.add_argument('--unc','-u'        , default='MuonEff, ElecEff, TrigEff'              , help = 'Uncertainty on backgrounds')
parser.add_argument('--norm','-n'       , default='1.30, 1.30, 1.30, 1.15, 1.06, 1.08'     , help = 'Uncertainty on backgrounds')
parser.add_argument('--signal','-s'     , default='stop'     , help = 'Signal process')
parser.add_argument('--lumiSyst','-l'   , default=0.025     , help = 'Uncertainty on luminosity')
parser.add_argument('--channel','-c'    , default="ElMu"     , help = 'Channel')

args = parser.parse_args()
verbose     = args.verbose
path        = args.path
filename    = args.filename
bkg         = args.bkg
unc         = args.unc
norm        = args.norm
signal      = args.signal
chan        = args.channel
lumisyst    = float(args.lumiSyst)

CreateDatacard(signal, path, filename, bkg, norm, lumisyst, unc, chan)
