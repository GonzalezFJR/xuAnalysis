# python GetLimits.py --year 2018 --chan emu --scan --significance --expSignal 1 --injectSignal stop_275_100
import os, argparse
from scipy.stats import norm

nslots   = 30
runblind = True
verbose  = True
years = [2016, 2017, 2018]
year = 0
ch = 'mumu'
datacardTag = ''#prueba
#pathToFiles = '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/stop_v629Mar/Unc/SR/%i/mass%i_%i/'
#pathToFilesComb = '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/stop_v629Mar/Unc/SR/comb/'

#pathToFiles     = '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/' + '16apr%s'%('_'+ch if ch in['ee', 'mumu'] else '') + '/Unc/SR/%i/mass%i_%i/'
#pathToFilesComb = '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/' + '16apr%s'%('_'+ch if ch in['ee', 'mumu'] else '') + '/Unc/SR/comb/'

#pathToFiles     = '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/' + '24may%s'%('_'+ch if ch in['ee', 'mumu'] else '') + '/Unc/SR/%i/mass%i_%i/'
#pathToFilesComb = '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/' + '24may%s'%('_'+ch if ch in['ee', 'mumu'] else '') + '/Unc/SR/comb/'

pathToModModul = '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/modules/DatacarModifier.py'
import imp

#trialFactor = 15.0378202114
nInd = 1.8 #2.24

scalettfact = 800./831.8

uncertainties = 'MuonEff, ElecEff, Trig, Btag, MuonES, Pref, TopPt, nongauss, Uncl, JESCor, JESUnCor, JER, PU, PDF, Scale, ISR, FSR'#, , JESCor, JESUnCor, JER'#, PU'#mtop, UE, hdamp,
parser = argparse.ArgumentParser(description='To select year and variable')
parser.add_argument('--year','-y',         default=year, help = 'Year')
parser.add_argument('--nSlots','-n',       default=nslots, help = 'Number of slots')
parser.add_argument('--mode','-m',       default='', help = 'Mode= "", "diag", "nodiag"')
parser.add_argument('--var','-v',          default='dnn', help = 'Variable')
parser.add_argument('--mStop','-s',        default=225, help = 'Stop mass')
parser.add_argument('--expSignal','--expecSignal',        default=1, help = 'Expected signal (for significance only)')
parser.add_argument('--mLSP','-l',         default=50, help = 'Neutralino mass')
parser.add_argument('--unblind','-u'     , action='store_true'  , help = 'Unblind')
parser.add_argument('--pretend','-p'     , action='store_true'  , help = 'Pretend')
parser.add_argument('--verbose',           action='store_true', help = 'Activate the verbosing')
parser.add_argument('--scan',              action='store_true', help = 'Produce the scan')
parser.add_argument('--chan','-c',         default='emu', help = 'Channel')
parser.add_argument('--significance','--sig', action='store_true'  , help = 'Do significance?')
parser.add_argument('--injectSignal',      default=''  , help = 'Inject signal name')
parser.add_argument('--impacts','-i',      action='store_true', help = 'Do impacts?')
parser.add_argument('--noDoCards','-x',      action='store_true', help = 'Force not to recreate cards')
parser.add_argument('--sufix',             default='', help = 'Re-create rootfiles and cards with modified parameters')
#args, unknown = parser.parse_known_args()
args = parser.parse_args()

ch = args.chan
year   = int(args.year) if args.year != 'comb' else 'comb'
nslots = int(args.nSlots)
var    = args.var
mStop  = int(args.mStop)
mLSP   = int(args.mLSP)
scan   = args.scan
doSignif = args.significance
noDoCards = args.noDoCards
expsignal = float(args.expSignal)
mode = args.mode
pretend = args.pretend
sufix = args.sufix

if args.unblind: runblind = False
if args.verbose: verbose  = True

getPathToComb = lambda ch, ms, ml: '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/29apr/Unc/SR/%s/comb/mass%i_%i/'%(ch, ms, ml)
getPathtoFiles = lambda ch, ms, ml, year: '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/29apr/Unc/SR/%s/%s/mass%i_%i/'%(ch, str(year), ms, ml)

#getPathToComb = lambda ch, ms, ml: '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/24may/Unc/SR/%s/comb/mass%i_%i/'%(ch, ms, ml)
#getPathtoFiles = lambda ch, ms, ml, year: '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/24may/Unc/SR/%s/%s/mass%i_%i/'%(ch, str(year), ms, ml)

signalSampleName = 'stop_test'
ttsampleName = 'tt_test'
if var == 'met': 
  signalSampleName = 'stop'
  ttsampleName = 'tt'

if args.injectSignal != '': signalSampleName = args.injectSignal

LumiUncertainties = {
  'Lumi2016'       : {2016 : 2.2, 2017 : 0.0, 2018 : 0.0},
  'Lumi2017'       : {2016 : 0.0, 2017 : 2.0, 2018 : 0.0},
  'Lumi2018'       : {2016 : 0.0, 2017 : 0.0, 2018 : 1.5},
  'XYfact'         : {2016 : 0.9, 2017 : 0.8, 2018 : 2.0},
  'LengthScale'    : {2016 : 0.0, 2017 : 0.3, 2018 : 0.2},
  'BeamBeamDefl'   : {2016 : 0.4, 2017 : 0.4, 2018 : 0.0},
  'DynamicBeta'    : {2016 : 0.5, 2017 : 0.5, 2018 : 0.0},
  'BeamCurrentCal' : {2016 : 0.0, 2017 : 0.3, 2018 : 0.2},
  'GhostAndSat'    : {2016 : 0.4, 2017 : 0.1, 2018 : 0.0},
}


variable = var#'metScanstop%i_%i_16000'
CraftDatacardName = lambda sig, var, sufix: 'datacard_%s%s_%s_ElMu%s.txt'%(var, '' if sufix=='' else '_'+sufix, signalSampleName, '_'+datacardTag if datacardTag!='' else '')#sig)
CraftSignalName   = lambda mst, mch : 'stop%i_%i'%(mst,mch)
dicDeac = 'Nonprompt:JES, Nonprompt:JER, Nonprompt:Uncl' if year == 2018 else ('')
for pr in ['DY','VV','ttW','ttZ', 'Nonprompt', 'tW', signalSampleName] : dicDeac = '%s:FSR, %s:ISR,'%(pr,pr) + dicDeac # ISR and FSR only for tt
#for pr in ['DY','VV','ttW','ttZ', 'Nonprompt', 'tW'] : dicDeac = '%s:JESCor, %s:JESUnCor, %s:JER, %s:PU,'%(pr,pr,pr,pr) + dicDeac # ISR and FSR only for tt
#for pr in ['Others','ttZ', 'Nonprompt', 'tW', signalSampleName] : dicDeac = '%s:FSR, %s:ISR,'%(pr, pr) + dicDeac # ISR and FSR only for tt
if dicDeac[-1] == ',': dicDeac = dicDeac[:-1]

def GetAllStopNeutralinoPoints(minStop = 145, maxStop = 295, dStop = 10, mindif = 145, maxdif = 205, ddif = 10, mode=''):
  points = []
  for mStop in range(minStop, maxStop+dStop, dStop):
    for dif in range(mindif, maxdif+ddif, ddif):
      mChi = mStop-dif
      #if mChi <= 10: continue
      if mode=='diag' and dif != 175: continue
      #if mChi >= 100: continue
      if mChi == 0: mChi = 1
      if mChi < 0 : continue
      if mStop+mChi > maxStop+(maxStop-maxdif): continue
      #print '[%i, %i]'%(mStop, mChi)
      #if mChi != 30 or mStop != 205: continue
      points.append([mStop, mChi])
  return points

def CreateDatacard(var = 'mt2', sig = 'stop275_100', path = 'rootfiles', sufix=''):
  pathToFile = '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/modules/CreateDatacards.py'
  #unc = 'MuonEff, ElecEff, Trig, Pref, MuonES, Btag, MisTag, TopPt, FSR, ISR, UE, PU, Uncl, JESCor, JESUnCor, JER' # mtop, hdamp
  #unc = 'MuonEff, ElecEff, Trig, Pref, MuonES, Btag, MisTag, TopPt, FSR, ISR, UE,  Uncl, JESCor, JESUnCor, hdamp' # mtop, hdamp
  unc  = uncertainties
  #norm = '1.30, 1.30, 1.30, 1.15, 1.035, 1.065'
  #bkg  = 'Others, ttZ, Nonprompt, tW, %s'%ttsampleName

  norm = '1.30, 1.30, 1.30, 1.30, 1.30, 1.15, 1.06, 1.065'
  bkg  = 'DY, ttW, VV, ttZ, Nonprompt, tW, %s'%ttsampleName

  #norm = '1.30, 1.30, 1.30, 1.30, 1.15, 1.06, 1.065'
  #bkg  = 'ttW, VV, ttZ, Nonprompt, tW, %s'%ttsampleName
  command = 'python %s %s%s -p %s -s %s -u "%s" -b "%s" -n "%s" -d "%s" %s%s'%(pathToFile, var, '' if sufix=='' else '_'+sufix, path, signalSampleName, unc, bkg, norm, dicDeac, '-t %s '%datacardTag if datacardTag!='' else '', '' if not verbose else '--verbose 1')
  if verbose: print 'Executing %s ...'%command
  os.system(command)

def ModiftRootfile(path, datacard, sufix):
  DM = imp.load_source('DatacardModifier', pathToModModul)
  #dm = DM.DatacardModifier(path, datacard, verbose=2, outsuf=sufix)
  #dm.RemoveNegativeYields('DY', uncertainties)
  #dm.RemoveNegativeYields('ttW', uncertainties)
  #dm.RemoveNegativeYields('VV', uncertainties)
  #dm.ScaleProcess(ttsampleName, uncertainties, scalettfact)

def ModifyBaseDatacard(path, datacard, year):
  DM = imp.load_source('DatacardModifier', pathToModModul)
  #print 'Reading datacard: %s'%(path+datacard)
  dm = DM.DatacardModifier(path, datacard, verbose=verbose)

  # Uncorrelate JESUnc
  dm.ReplaceLabel('JESUnCor', 'JESUnCor%i'%year)
  dm.RenameSystInHistos('JESUnCor', 'JESUnCor%i'%year)

  # Uncorrelate JER
  dm.ReplaceLabel('JER', 'JER%i'%year)
  dm.RenameSystInHistos('JER', 'JER%i'%year)

  # Uncorrelate Uncl energy
  dm.ReplaceLabel('Uncl', 'Uncl%i'%year)
  dm.RenameSystInHistos('Uncl', 'Uncl%i'%year)

  # Uncorrelate lumi
  nline = dm.FindLineStart('Lumi')
  for lumiunc in LumiUncertainties:
    val = LumiUncertainties[lumiunc][year]
    if val == 0.: continue
    val = 1+float(val)/100
    dm.AddLine(dm.UncForAllProcesses(lumiunc + ' lnN ', val), nline)
  dm.RmLineStart('Lumi', True)

  # Uncorrelate tt Tune, FSR, hdamp and PDFTuneCUETP8M2T4
  UElab = 'UE%s'%('TuneCUETP8M2T4' if year == 2016 else 'TuneCP5')
  dm.ReplaceLabel('UE',  UElab)
  dm.RenameSystInHistos('UE', UElab)
  if year == 2016: 
    for unc in ['PDF', 'FSR', 'hdamp']:
      dm.ReplaceLabel(unc, unc+'2016')
      dm.RenameSystInHistos(unc, unc+'2016')
  dm.save()

def CombineCards(cards, outname):
  command = 'combineCards.py '
  for c in cards: command += c + ' '
  command += ' > %s'%(outname)
  os.system(command)
  if verbose: print 'Created card %s'%(outname)

def GetAsympLimit(datacard, mstop = 0, tag=''):
  command = 'combine -M AsymptoticLimits -n stopLimites%s -m %s %s --X-rtd MINIMIZER_analytic %s'%(tag, mstop, '--run blind -t -1' if runblind else '', datacard)
  if verbose: print 'Executing combine: ', command
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

def GetSignificance(datacard, mstop=0, expsignal=1):
  command = 'combine -M Significance -t -1 --expectSignal %f -m %s --X-rtd MINIMIZER_analytic %s'%(float(expsignal), str(mstop), datacard)
  if verbose: print 'Executing combine: ', command
  out = os.popen(command).read()
  n = out.find('Significance:')
  dataline = out[n:].split('\n')[0]
  val = float(dataline[dataline.index('Significance:')+len('Significance:'):])
  # Transform to global
  # sqrt(pi/2) = 
  trialFactor = 1.2533141373155001*nInd*val
  glob = norm.ppf(1-trialFactor*(1-norm.cdf(val)))
  if glob > 1000: glob=val 
  if val > 9: glob=val 
  return val, glob

def DoCard(mstop, mlsp = 0, var = 'dnn', year=2018, chan='emu', docard=True, sufix=''):
  if '%i' in var: var = var%(mstop, mlsp)
  if '%i' in var: var = var%(mstop, mlsp)
  chan = [ch] if ch!='all' else ['ee', 'mumu', 'emu']
  years = [year] if year in [2016, 2017, 2018] else [2016, 2017, 2018]
  sname    = CraftSignalName(mstop, mlsp)
  datacard = CraftDatacardName(sname, var, sufix)
  if len(years) == 1 and len(chan) == 1: outpath = getPathtoFiles(ch, mstop, mlsp, year)
  else: outpath = (getPathToComb(ch, mstop, mlsp)) if ch != 'all' else  (getPathToComb('emu',mstop,mlsp)+'mass%i_%i/allChan/'%(mstop, mlsp))
  if not docard: return outpath+'/'+datacard
  if len(years) == 1 and len(chan) == 1:
    path = getPathtoFiles(ch, mstop, mlsp, year)
    if sufix != '': ModiftRootfile(path, CraftDatacardName(sname, var, ''), sufix)
    CreateDatacard(var, sname, path, sufix=sufix)
    ModifyBaseDatacard(path,datacard, year)
  else:
    cards = []
    for y in years:
      for c in chan:
        path = getPathtoFiles(c, mstop, mlsp, y)
        if sufix != '': ModiftRootfile(path, CraftDatacardName(sname, var, ''), sufix)
        CreateDatacard(var, sname, path, sufix=sufix)
        ModifyBaseDatacard(path,datacard, y)
        cards.append(path + datacard)
      outpath = (getPathToComb(ch, mstop, mlsp)) if ch != 'all' else  (getPathToComb('emu',mstop,mlsp)+'mass%i_%i/allChan/'%(mstop, mlsp))
      path = outpath
      os.system('mkdir -p %s'%outpath)
      CombineCards(cards, outpath+datacard)
  print 'Created card: ', path+'/'+datacard
  return path + '/' + datacard

def GetLimitsForMass(mstop, mlsp = 0, var = 'metScanstop%i_%i_16000', path = 'rootfiles', verbose=False):
  if isinstance(mstop, list): 
    if   len(mstop) == 2: mstop, mlsp            = mstop
    elif len(mstop) == 3: mstop, mlsp, var       = mstop
    elif len(mstop) == 4: mstop, mlsp, var, path = mstop
  var = variable
  if '%i' in var: var = var%(mstop, mlsp)
  datacard = DoCard(mstop, mlsp, var, year, ch, not noDoCards, sufix)
  limits = GetAsympLimit(datacard, mstop, '%s%s'%(str(ch), str(year))) if not doSignif else GetSignificance(datacard, mstop, expsignal)
  if verbose: print [mstop, mlsp, limits]
  return [mstop, mlsp, limits]

def main():
  if not scan: 
    GetLimitsForMass(mStop, mLSP, var, verbose=True)
    exit()
  masses = GetAllStopNeutralinoPoints(minStop = 145, maxStop = 295, dStop = 10, mindif = 145, maxdif = 205, ddif = 10, mode=mode)#diag')

  from multiprocessing import Pool
  listInput = masses
  pool = Pool(nslots)
  if ch == 'all': 
    results = pool.map(GetLimitsForMass, listInput)
  else:
    results = pool.map(GetLimitsForMass, listInput)
  pool.close()
  pool.join()
  
  import pickle
  varname = variable if not '%i' in variable else variable.replace('%i', '').replace('_', '')
  pickle.dump( results, open( "%s_%s_%s%s.p"%('limits' if not doSignif else 'significance', str(year) if year != 0 else 'comb', varname, '_%s'%ch if ch in ['ee', 'mumu', 'all'] else ''), "wb" ) )
  print results

if __name__ == '__main__':
  main()
 
