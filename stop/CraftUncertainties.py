import os, sys
from config import *
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)
from config import *
import imp
from ROOT import TFile

hists = ['mt2','met', 'mll', 'dnn', 'dileppt', 'deltaphi', 'deltaeta', 'ht', 'lep0pt', 'lep1pt', 'lep0eta', 'lep1eta', 'njets', 'nbtags']
verbose = False

pathToModModul = '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/modules/DatacarModifier.py'
mod = imp.load_source('DatacardModifier', pathToModModul)
GetDiffSystNom = mod.GetDiffSystNom
ApplyDifsToNom = mod.ApplyDifsToNom

import argparse
parser = argparse.ArgumentParser(description='To select masses and year')
parser.add_argument('--year','-y',         default=2018   , help = 'Year')
parser.add_argument('--mStop',        default=225  , help = 'Stop mass')
parser.add_argument('--mLSP',         default= 50  , help = 'Neutralino mass')
parser.add_argument('--region',       default='SR'  , help = 'Select the region')
parser.add_argument('--chan','-c',       default='emu'  , help = 'Select the channel')
 
args, unknown = parser.parse_known_args()

ms   = int(args.mStop)
ml   = int(args.mLSP)
year = int(args.year)
region = args.region
chan = args.chan

path = {}
path[year] = pathToTrees(year, chan, region)

# Set constants
GetSubfolder = lambda region, chan, year, ms, ml : '/%s/%s/%i/mass%i_%i/'%(region, chan, year, ms, ml)
subfolder = GetSubfolder(region, chan, year, ms, ml)

GetFolder = lambda folder : baseoutpath+'/%s/'%folder+subfolder

def GetHistoFromFile(fname, hname):
  f = TFile.Open(fname)
  if not hasattr(f, hname):
    print 'WARNING: not histogram %s found in %s'%(hname, fname)
  h = f.Get(hname)
  h.SetDirectory(0)
  f.Close()
  return h

def ExistsHistoInFile(fname, hname):
  f = TFile.Open(fname)
  has = hasattr(f, hname)
  f.Close()
  return f

def AddHistsToFile(fname, hists, verbose=False):
  f = TFile.Open(fname, 'UPDATE')
  for h in hists: 
    if verbose: print ' >> Adding histogram %s'%h.GetName()
    h.Write()
  f.Close()

def RemoveNegativeBins(fname, hists, verbose=False):
  f = TFile.Open(fname, 'UPDATE')
  for hn in hists: 
    if not hasattr(f, hn): continue
    h = f.Get(hn)
    nbins = h.GetNbinsX()
    for i in range(0,nbins+1):
      c = h.GetBinContent(i)
      e = h.GetBinError(i)
      if c<0: h.SetBinContent(i, 0)
      if e<0: h.SetBinErorr(i, abs(e))
    if verbose: print ' >> Modifying histogram %s'%h.GetName()
    h.Write()
  f.Close()

def GetUncAndAdd(varname, inpath, outpath, sysname, namenom, newname = '', nameup='', namedo='', verbose=False):
  if not varname.endswith('.root'): varname += '.root'
  if newname == '': newname = namenom
  if nameup  == '': nameup  = namenom+'_%s%s'%(sysname, 'Up')
  if namedo  == '': namedo  = namenom+'_%s%s'%(sysname, 'Down')

  hnom = GetHistoFromFile(inpath+varname, namenom)
  hup  = GetHistoFromFile(inpath+varname, nameup )
  hdo  = GetHistoFromFile(inpath+varname, namedo )
  updif, dodif = GetDiffSystNom(hnom, hup, hdo)

  htarget = GetHistoFromFile(outpath+varname, newname)
  hn, hu, hd = ApplyDifsToNom(htarget, updif, dodif, sysname, newname)
  AddHistsToFile(outpath+varname, [hu, hd], verbose)

def AddHistoUncToTest(varname, path, frompr='tt', pr='tt_test', syst='hdamp', verbose=False):
  if not path.endswith('/'): path+='/'
  fname = path+varname
  if not fname.endswith('.root'): fname+= '.root'
  if not os.path.isfile(fname):
    print 'ERROR: file "%s" not found'%fname
  hup = GetHistoFromFile(fname, '%s_%sUp'   %(frompr,syst))
  hdo = GetHistoFromFile(fname, '%s_%sDown' %(frompr,syst))
  hn  = GetHistoFromFile(fname, frompr)
  hnom= GetHistoFromFile(fname, pr)
  updif, dodif = GetDiffSystNom(hn, hup, hdo)
  hnom, hu, hd = ApplyDifsToNom(hnom, updif, dodif, syst, pr)
  if varname=='dnn':
    #print syst, ', up = ', updif, ', do = ', dodif
    print '%s [nom, up, do]  = [%1.2f, %1.2f, %1.2f]'%(syst, hnom.Integral(), hu.Integral(), hd.Integral())
  hu.SetName('%s_%sUp'  %(pr,syst))
  hd.SetName('%s_%sDown'%(pr,syst))
  AddHistsToFile(fname, [hu, hd], verbose)
  

def AddNonGaussUnc(varname, pathNom, pathSyst, hname='ttnongauss', systname = 'nongauss', unc=0.3, pr = 'tt', verbose=False):
  if not varname.endswith('.root'): varname += '.root'
  htarget = GetHistoFromFile(pathNom+varname, pr)

  hnongauss = GetHistoFromFile(pathSyst+varname, hname)
  hup = hnongauss.Clone('tt_%sUp'  %systname)
  hdo = hnongauss.Clone('tt_%sDown'%systname)
  hup.Scale(1+unc)
  hdo.Scale(1-unc)
  updif, dodif = GetDiffSystNom(hnongauss, hup, hdo)

  htaget = GetHistoFromFile(pathNom+varname, pr)
  hn, hu, hd = ApplyDifsToNom(htarget, updif, dodif, systname, pr, doAbsolute=True)
  AddHistsToFile(pathNom+varname, [hu, hd], verbose)
  

pathToRootfiles = GetFolder('/Unc/')
pathToFSR2016files = GetFolder('/Unc_FSR/')
pathToPDFfiles = GetFolder('PDFunc')

verbose = False
if verbose:
  print 'Variables: ', hists
  print 'Target   : ', pathToRootfiles
  print 'Systs    : ', pathToPDFfiles
for var in hists:
  for pr in ['tt', 'tt_test']:
    GetUncAndAdd(var, pathToPDFfiles+'/PDF/', pathToRootfiles, 'PDF', 'tt', pr, verbose=verbose)
    GetUncAndAdd(var, pathToPDFfiles+'/Scale/', pathToRootfiles, 'Scale', 'tt', pr, verbose=verbose)
    if year == 2016:
      GetUncAndAdd(var, pathToFSR2016files, pathToRootfiles, 'ISR', 'tt', pr, verbose=verbose)
      GetUncAndAdd(var, pathToFSR2016files, pathToRootfiles, 'FSR', 'tt', pr,  verbose=verbose)
    AddNonGaussUnc(var, pathToRootfiles,    pathToRootfiles, hname='ttnongauss', systname='nongauss', unc=0.3, pr=pr, verbose=verbose)
  for syst in ['hdamp', 'mtop', 'UE']:
    AddHistoUncToTest(var, pathToRootfiles, 'tt', 'tt_test', syst, verbose=verbose)
