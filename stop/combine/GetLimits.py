import os

nslots   = 30
runblind = True
verbose  = False

CraftDatacardName = lambda sig, var : 'datacard_%s_%s_ElMu.txt'%(var, sig)
CraftSignalName   = lambda mst, mch : 'stop'#%i_%i'%(mst,mch)
dicDeac = 'Nonprompt:JES, Nonprompt:JER'

def GetAllStopNeutralinoPoints(minStop = 145, maxStop = 295, dStop = 10, mindif = 145, maxdif = 205, ddif = 10):
  points = []
  for mStop in range(minStop, maxStop+dStop, dStop):
    for dif in range(mindif, maxdif+ddif, ddif):
      mChi = mStop-dif
      if mChi <= 10: continue
      #if dif != 175: continue
      #if mChi >= 100: continue
      if mChi == 0: mChi = 1
      if mStop+mChi > maxStop+(maxStop-maxdif): continue
      #print '[%i, %i]'%(mStop, mChi)
      points.append([mStop, mChi])
  return points

def CreateDatacard(var = 'mt2', sig = 'stop275_100', path = 'rootfiles'):
  pathToFile = '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/modules/CreateDatacards.py'
  unc  = 'MuonEff, ElecEff, Trig, Pref, JES, JER, Uncl, MuonES, Btag, MisTag, PU, UE, hdamp, TopPt'
  norm = '1.30, 1.30, 1.15, 1.06, 1.08'
  bkg  = 'ttZ, Nonprompt, tW, tt'
  command = 'python %s %s -p %s -s %s -u "%s" -b "%s" -n "%s" -d "%s"'%(pathToFile, var, path, sig, unc, bkg, norm, dicDeac)
  if verbose: print 'Executing %s ...'%command
  os.system(command)

def GetAsympLimit(datacard, mstop = 0):
  command = 'combine -M AsymptoticLimits -n stopLimites -m %s %s-t -1 --X-rtd MINIMIZER_analytic %s'%(mstop, '--run blind ' if runblind else '', datacard)
  out = os.popen(command).read()
  n = out.find('Expected  2.5%: r <')
  m = out.find('Observed Limit: r <')
  dataline = out[m:].split('\n')[0]
  out = out[n:]
  limits = out.split('\n')
  if not runblind:
    limits.append(dataline)
  outlist = []
  for line in limits:
    n = line.find('r < ')
    if n < 0: continue
    res = float(line[n+4:])
    outlist.append(res)
  return outlist

def GetLimitsForMass(mstop, mlsp = 0, var = 'metScanstop%i_%i_16000', path = 'rootfiles'):
  if isinstance(mstop, list): 
    if   len(mstop) == 2: mstop, mlsp            = mstop
    elif len(mstop) == 3: mstop, mlsp, var       = mstop
    elif len(mstop) == 4: mstop, mlsp, var, path = mstop
  if '%i' in var: var = var%(mstop, mlsp)
  sname    = CraftSignalName(mstop, mlsp)
  datacard = CraftDatacardName(sname, var)
  path = '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/stop/Unc/SR/mass%i_%i/'%(mstop, mlsp)
  CreateDatacard(var, sname, path)
  limits = GetAsympLimit(path + '/' + datacard, mstop)
  return [mstop, mlsp, limits]
  
masses = GetAllStopNeutralinoPoints(minStop = 145, maxStop = 295, dStop = 10, mindif = 145, maxdif = 205, ddif = 10)

from multiprocessing import Pool
listInput = masses
pool = Pool(nslots)
results = pool.map(GetLimitsForMass, listInput)
pool.close()
pool.join()

import pickle
pickle.dump( results, open( "limits.p", "wb" ) )

print results
