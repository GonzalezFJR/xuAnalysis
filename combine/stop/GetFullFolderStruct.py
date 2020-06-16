import os, sys
from GetLimits import GetAllStopNeutralinoPoints
basepath = '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/29apr/Unc/SR/'
foldername = lambda ch, y, ms, ml: '%s/%s/mass%s_%s/'%(ch, str(y), str(ms), str(ml))
filename = lambda var : '%s.root'%var
combpath = lambda ms, ml : 'emu/comb/mass%s_%s/mass%s_%s/allChan/'%(str(ms), str(ml), str(ms), str(ml))
olddatacard = lambda var : 'datacard_%s_stop_test_ElMu.txt'%var
datacardname = lambda ms, ml, var : 'datacard_stop2l_%s_%s_%s.txt'%(var, str(ms), str(ml))

var = 'dnn'
allmasses = GetAllStopNeutralinoPoints()
channels = ['emu', 'ee', 'mumu']
years = [2016, 2017, 2018]

# Create output path
outpath = 'stopCorridor/'
os.system('mkdir -p %s'%outpath)

# Modify paths in datacards
pathToModModul = '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/modules/DatacarModifier.py'
import imp
DM = imp.load_source('DatacardModifier', pathToModModul)

def mvcard(ms, ml, var):
  path = basepath+combpath(ms, ml)
  datacard = olddatacard(var)
  dm = DM.DatacardModifier(path, datacard, verbose=0)
  dm.SetOutPath(outpath)
  dm.SetDatacOutName(datacardname(ms,ml,var))
  for y in years:
    for ch in channels:
      bpath = basepath + foldername(ch, y, ms, ml) + filename(var)
      opath = foldername(ch, y, ms, ml) + filename(var)
      dm.ReplacePathToFiles(bpath, opath)
  dm.save()

#ms = 225; ml = 50; ch = 'ee'; y = 2016
#mvcard(ms, ml, var)
#exit()

# Copy all the datacards
for ms,ml in allmasses:
  #command = 'cp %s%s%s %s%s'%(basepath, combpath(ms,ml,var), olddatacard(var), outpath, datacardname(ms, ml, var))
  #os.system(command)
  mvcard(ms,ml,var)

# Create structure of folders and copy files
for ms,ml in allmasses:
  for y in years:
    for ch in channels:
      folder = foldername(ch, y, ms, ml)
      mkdir = 'mkdir -p %s%s'%(outpath, folder)
      os.system(mkdir)
      cpcommand = 'cp %s%s%s %s%s'%(basepath, folder, filename(var), outpath, folder)
      os.system(cpcommand)

